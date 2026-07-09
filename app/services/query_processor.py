from datetime import datetime, time
from typing import List, Optional
from beanie import PydanticObjectId
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool

from core.config import settings
from models.request import ChatMessage
from models.response import ChatResponse
from services.llm_provider import get_llm
from services.prompt_builder import get_system_prompt

def create_agent_tools(user_id: PydanticObjectId, raw_input_text: str = ""):
    """
    Creates custom tools bound securely to the authenticated user's ID.
    This guarantees data isolation between different users.
    """

    @tool
    async def log_transaction(
        amount: float,
        category: str,
        payment_method: Optional[str] = "UPI",
        merchant: Optional[str] = "",
        transaction_date: Optional[str] = None,
        description: Optional[str] = ""
    ) -> str:
        """
        Logs and records an expense transaction to the database.
        Use this tool when the user explicitly wants to record/add/log an expense.
        
        Parameters:
        - amount: Float. The numeric cost of the transaction. Required and must be positive.
        - category: String. Predefined category. Must match one of: "Food & Dining", "Shopping", "Travel & Transport", "Bills & Utilities", "Entertainment", "Health & Medical", "Others".
        - payment_method: String. Predefined payment method. Must match one of: "Cash", "Card", "UPI". Defaults to "UPI".
        - merchant: String. The name of the store, vendor, or merchant.
        - transaction_date: String. ISO 8601 string (e.g. 2026-07-08T12:00:00Z). Resolve relative dates first.
        - description: String. Additional comments or context.
        """
        from services.transaction import create_transaction
        from models.request import TransactionCreateRequest
        from models.db_transaction import TransactionCategory, PaymentMethod, LLMMetadata

        # Resolve transaction date
        tx_date = datetime.utcnow()
        if transaction_date:
            try:
                # Remove Z and parse to datetime
                clean_date = transaction_date.replace("Z", "+00:00")
                tx_date = datetime.fromisoformat(clean_date)
            except Exception:
                pass  # Default to current time on parsing error

        # Map category safely to Enum
        try:
            mapped_category = TransactionCategory(category)
        except ValueError:
            mapped_category = TransactionCategory.OTHERS

        # Map payment method safely to Enum
        try:
            mapped_payment = PaymentMethod(payment_method)
        except ValueError:
            mapped_payment = PaymentMethod.UPI

        request_data = TransactionCreateRequest(
            amount=amount,
            category=mapped_category,
            payment_method=mapped_payment,
            merchant=merchant or "",
            transaction_date=tx_date,
            description=description or "",
            source_type="llm",
            llm_metadata=LLMMetadata(raw_input_text=raw_input_text) if raw_input_text else None
        )

        try:
            tx = await create_transaction(user_id, request_data)
            return (
                f"Success: Recorded transaction. ID: {tx.id}, Amount: {tx.amount}, "
                f"Category: {tx.category.value}, Merchant: {tx.merchant or 'None'}, "
                f"Date: {tx.transaction_date.strftime('%Y-%m-%d %H:%M:%S')}."
            )
        except Exception as e:
            return f"Error writing to database: {str(e)}"

    @tool
    async def query_database(
        category: Optional[str] = None,
        payment_method: Optional[str] = None,
        merchant: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> str:
        """
        Queries the user's historical transactions database to answer questions about spending.
        Use this tool when the user asks analytical queries like "how much did I spend", "show my bills", "find transactions".
        
        Parameters:
        - category: String. Optional category filter.
        - payment_method: String. Optional payment method filter.
        - merchant: String. Optional merchant keyword (performs case-insensitive partial match).
        - start_date: String. Optional start date filter in 'YYYY-MM-DD' format.
        - end_date: String. Optional end date filter in 'YYYY-MM-DD' format.
        - min_amount: Float. Optional minimum amount filter.
        - max_amount: Float. Optional maximum amount filter.
        """
        from models.db_transaction import Transaction

        # Build base query scoped to this user
        query = Transaction.find(Transaction.user_id == user_id)

        # Apply optional filters
        if category:
            query = query.find(Transaction.category == category)
        if payment_method:
            query = query.find(Transaction.payment_method == payment_method)
        if merchant:
            query = query.find({"merchant": {"$regex": merchant, "$options": "i"}})
        if start_date:
            try:
                start_dt = datetime.combine(datetime.strptime(start_date, "%Y-%m-%d"), time.min)
                query = query.find(Transaction.transaction_date >= start_dt)
            except Exception:
                pass
        if end_date:
            try:
                end_dt = datetime.combine(datetime.strptime(end_date, "%Y-%m-%d"), time.max)
                query = query.find(Transaction.transaction_date <= end_dt)
            except Exception:
                pass
        if min_amount is not None:
            query = query.find(Transaction.amount >= min_amount)
        if max_amount is not None:
            query = query.find(Transaction.amount <= max_amount)

        # Limit to 50 items to keep token length safe
        transactions = await query.sort(-Transaction.transaction_date).limit(50).to_list()

        if not transactions:
            return "No matching transactions found in the database."

        # Format output
        results_lines = []
        total = 0.0
        for tx in transactions:
            total += tx.amount
            results_lines.append(
                f"- Date: {tx.transaction_date.strftime('%Y-%m-%d')} | "
                f"Amount: {tx.amount:.2f} | Merchant: {tx.merchant or 'None'} | "
                f"Category: {tx.category.value} | PM: {tx.payment_method.value} | "
                f"Desc: {tx.description or 'None'}"
            )

        summary = f"Found {len(transactions)} transactions. Total Amount: {total:.2f}.\n" + "\n".join(results_lines)
        return summary

    return [log_transaction, query_database]

async def process_chat(
    user_id: PydanticObjectId,
    message: str,
    history: List[ChatMessage]
) -> ChatResponse:
    """
    Executes the conversational agent loop. Binds tools to the user_id, loads recent history,
    runs the executor via Gemini, and parses the output and tool metadata.
    """
    # 1. Initialize the LLM (gemini-2.5-flash) and bind our tools
    llm = get_llm(temperature=0.0)
    tools = create_agent_tools(user_id, raw_input_text=message)
    llm_with_tools = llm.bind_tools(tools)

    # 2. Setup message history starting with system instruction
    system_instruction = get_system_prompt(datetime.utcnow())
    messages = [SystemMessage(content=system_instruction)]

    # 3. Append historical user & assistant messages
    for msg in history:
        if msg.role == "user":
            messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            messages.append(AIMessage(content=msg.content))

    # 4. Append current user message
    messages.append(HumanMessage(content=message))

    # 5. Run the tool-calling loop
    try:
        # First turn: Gemini decides if a tool should be triggered
        response = await llm_with_tools.ainvoke(messages)

        tool_triggered = None
        metadata = {}

        if response.tool_calls:
            # We support one tool call per turn for simplicity and speed
            tool_call = response.tool_calls[0]
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            tool_id = tool_call["id"]

            tool_triggered = tool_name
            metadata = {
                "query_filters": tool_args
            }

            # Find the matching tool object
            tool_obj = next((t for t in tools if t.name == tool_name), None)
            if tool_obj:
                # Execute the tool asynchronously
                tool_output = await tool_obj.ainvoke(tool_args)

                # Parse count of items from the output if querying the database
                results_count = 1
                if isinstance(tool_output, str) and "Found" in tool_output:
                    results_count = len([l for l in tool_output.split("\n") if l.startswith("- Date:")])
                metadata["results_count"] = results_count

                # Append the assistant's tool-call request and the tool's response to message history
                messages.append(response)
                messages.append(ToolMessage(content=tool_output, tool_call_id=tool_id))

                # Second turn: Gemini synthesizes the final response incorporating the tool outputs
                final_response = await llm_with_tools.ainvoke(messages)
                output_text = final_response.content
            else:
                output_text = "Error: Triggered tool could not be executed."
        else:
            # No tool was triggered; direct conversational response
            output_text = response.content

        return ChatResponse(
            response=output_text,
            tool_triggered=tool_triggered,
            metadata=metadata
        )

    except Exception as e:
        return ChatResponse(
            response=f"Sorry, I encountered an error while processing: {str(e)}",
            tool_triggered=None,
            metadata={"error": str(e)}
        )

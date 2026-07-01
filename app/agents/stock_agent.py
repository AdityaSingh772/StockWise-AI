import logging
from app.graph.state import WorkflowState
from app.graph.workflow import run_workflow
from app.models.schemas import AnalysisRequest, AnalysisResponse

logger = logging.getLogger(__name__)


class StockAnalysisAgent:
    """
    High-level agent that orchestrates the stock analysis workflow.
    This acts as the primary interface between the API/bot and the
    underlying LangGraph workflow.
    """

    async def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        """
        Run a full stock analysis for the given request.
        Returns an AnalysisResponse with the formatted report.
        """
        logger.info(
            f"StockAnalysisAgent.analyze | chat_id={request.chat_id} | "
            f"query='{request.user_message}'"
        )

        result = await run_workflow(
            user_message=request.user_message,
            chat_id=request.chat_id,
            user_name=request.user_name,
        )

        return AnalysisResponse(
            success=result.get("success", False),
            report=result.get("report"),
            error=result.get("error"),
            ticker=result.get("ticker"),
            company_name=result.get("company_name"),
        )

"""Facade for LLM monitoring and evaluation."""

from typing import Any, Dict, List, Optional, Union

import pandas as pd

from .factory import create_llm_monitor
from .ml_monitor import MLMonitor


class LLMMonitor:
    """
    Facade for LLM monitoring and evaluation.

    This class serves as an entry point for all LLM monitoring functionality,
    providing a unified interface regardless of the underlying implementation.
    """

    def __init__(
        self,
        mlflow_client=None,
        ml_monitor: Optional[MLMonitor] = None,
        provider: str = "evidently",
    ):
        """
        Initialize the LLMMonitor facade.

        Args:
            mlflow_client: MLflowClient instance for logging metrics
            ml_monitor: Optional MLMonitor instance to share functionality
            provider: The provider to use for monitoring implementation
        """
        # If ml_monitor is provided, use its underlying monitor for shared functionality
        underlying_ml_monitor = ml_monitor.monitor if ml_monitor else None

        self._monitor = create_llm_monitor(
            provider=provider,
            mlflow_client=mlflow_client,
            ml_monitor=underlying_ml_monitor,
        )

    def create_column_mapping(
        self,
        datetime_col: Optional[str] = None,
        prompt_col: str = "prompt",
        response_col: str = "response",
        reference_col: Optional[str] = None,
        categorical_cols: Optional[List[str]] = None,
        datetime_cols: Optional[List[str]] = None,
        numerical_cols: Optional[List[str]] = None,
    ) -> Any:
        """
        Create a column mapping for LLM evaluation.

        Args:
            datetime_col: The datetime column for time-based analysis
            prompt_col: Column name for the prompt/question
            response_col: Column name for the model response
            reference_col: Column name for reference/golden response
            categorical_cols: List of categorical feature columns
            datetime_cols: List of datetime feature columns
            numerical_cols: List of numerical feature columns

        Returns:
            Any: Column mapping configuration
        """
        return self._monitor.create_column_mapping(
            datetime_col=datetime_col,
            prompt_col=prompt_col,
            response_col=response_col,
            reference_col=reference_col,
            categorical_cols=categorical_cols,
            datetime_cols=datetime_cols,
            numerical_cols=numerical_cols,
        )

    def evaluate_text_length(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[Any] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Any:
        """
        Evaluate text length metrics for LLM responses.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files

        Returns:
            Any: The report object
        """
        return self._monitor.evaluate_text_length(
            data=data,
            response_col=response_col,
            reference_data=reference_data,
            column_mapping=column_mapping,
            save_html=save_html,
            output_path=output_path,
        )

    def evaluate_content_patterns(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        words_to_check: Optional[List[str]] = None,
        patterns_to_check: Optional[List[str]] = None,
        prefix_to_check: Optional[str] = None,
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[Any] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Any:
        """
        Evaluate content patterns in LLM responses.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            words_to_check: List of words to check for in responses
            patterns_to_check: List of patterns to check for in responses
            prefix_to_check: Prefix to check for in responses
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files

        Returns:
            Any: The report object
        """
        return self._monitor.evaluate_content_patterns(
            data=data,
            response_col=response_col,
            words_to_check=words_to_check,
            patterns_to_check=patterns_to_check,
            prefix_to_check=prefix_to_check,
            reference_data=reference_data,
            column_mapping=column_mapping,
            save_html=save_html,
            output_path=output_path,
        )

    def create_comparison_visualization(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        output_path: str = "./reports",
        response_col: str = "response",
        metrics: Optional[List[str]] = None,
        artifact_path: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> str:
        """
        Create visualizations comparing reference and current data.

        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            output_path: Directory to save visualization files
            response_col: Column name containing the response text
            metrics: List of metrics to visualize
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            str: Path to the saved visualization file
        """
        return self._monitor.create_comparison_visualization(
            reference_data=reference_data,
            current_data=current_data,
            output_path=output_path,
            response_col=response_col,
            metrics=metrics,
            artifact_path=artifact_path,
            run_id=run_id,
        )

    def evaluate_semantic_properties(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        prompt_col: Optional[str] = "prompt",
        check_sentiment: bool = True,
        check_toxicity: bool = True,
        check_prompt_relevance: bool = True,
        huggingface_models: Optional[List[Dict[str, Any]]] = None,
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[Any] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Any:
        """
        Evaluate semantic properties of LLM responses.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            prompt_col: Column name containing prompts/questions
            check_sentiment: Whether to check sentiment
            check_toxicity: Whether to check toxicity
            check_prompt_relevance: Whether to check prompt-response relevance
            huggingface_models: List of custom HuggingFace models to use
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files

        Returns:
            Any: The report object
        """
        return self._monitor.evaluate_semantic_properties(
            data=data,
            response_col=response_col,
            prompt_col=prompt_col,
            check_sentiment=check_sentiment,
            check_toxicity=check_toxicity,
            check_prompt_relevance=check_prompt_relevance,
            huggingface_models=huggingface_models,
            reference_data=reference_data,
            column_mapping=column_mapping,
            save_html=save_html,
            output_path=output_path,
        )

    def evaluate_llm_as_judge(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        check_pii: bool = True,
        check_decline: bool = True,
        custom_evals: Optional[List[Dict[str, Any]]] = None,
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[Any] = None,
        save_html: bool = False,
        output_path: str = "./reports",
    ) -> Optional[Any]:
        """
        Evaluate LLM responses using LLM-as-judge.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            check_pii: Whether to check for PII in responses
            check_decline: Whether to check if responses decline to answer
            custom_evals: List of custom evaluation criteria
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files

        Returns:
            Any: The report object or None if LLM judge is not available
        """
        return self._monitor.evaluate_llm_as_judge(
            data=data,
            response_col=response_col,
            check_pii=check_pii,
            check_decline=check_decline,
            custom_evals=custom_evals,
            reference_data=reference_data,
            column_mapping=column_mapping,
            save_html=save_html,
            output_path=output_path,
        )

    def create_test_suite(
        self,
        response_col: str = "response",
        min_response_length: int = 1,
        max_response_length: int = 2000,
        min_sentiment: float = 0.0,
        min_mean_response_length: int = 100,
    ) -> Any:
        """
        Create a test suite for LLM responses with conditions to check.

        Args:
            response_col: Column name containing model responses
            min_response_length: Minimum acceptable response length
            max_response_length: Maximum acceptable response length
            min_sentiment: Minimum acceptable sentiment score
            min_mean_response_length: Minimum acceptable mean response length

        Returns:
            Any: The test suite object
        """
        return self._monitor.create_test_suite(
            response_col=response_col,
            min_response_length=min_response_length,
            max_response_length=max_response_length,
            min_sentiment=min_sentiment,
            min_mean_response_length=min_mean_response_length,
        )

    def generate_dashboard(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        category_col: Optional[str] = "category",
        model_col: Optional[str] = "model",
        sentiment_col: Optional[str] = "sentiment_score",
        output_path: str = "./reports",
        dashboard_name: str = "response_quality_dashboard.png",
        artifact_path: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> str:
        """
        Create a dashboard visualization of LLM response data.

        Args:
            data: DataFrame containing the LLM responses
            response_col: Column containing the text responses
            category_col: Column containing response categories
            model_col: Column containing model names
            sentiment_col: Column containing sentiment scores
            output_path: Directory to save the dashboard
            dashboard_name: Filename for the dashboard image
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            str: Path to the generated dashboard
        """
        return self._monitor.generate_dashboard(
            data=data,
            response_col=response_col,
            category_col=category_col,
            model_col=model_col,
            sentiment_col=sentiment_col,
            output_path=output_path,
            dashboard_name=dashboard_name,
            artifact_path=artifact_path,
            run_id=run_id,
        )

    def generate_summary_report(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        output_path: str = "./reports",
        report_name: str = "evaluation_summary.html",
        include_cols: Optional[List[str]] = None,
        artifact_path: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> str:
        """
        Generate an HTML summary report for LLM responses.

        Args:
            data: DataFrame containing the LLM responses
            response_col: Column containing the text responses
            output_path: Directory to save the report
            report_name: Filename for the HTML report
            include_cols: Additional columns to include in the report
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            str: Path to the generated report
        """
        return self._monitor.generate_summary_report(
            data=data,
            response_col=response_col,
            output_path=output_path,
            report_name=report_name,
            include_cols=include_cols,
            artifact_path=artifact_path,
            run_id=run_id,
        )

    def generate_comparison_report(
        self,
        reference_data: pd.DataFrame,
        current_data: pd.DataFrame,
        response_col: str = "response",
        category_col: Optional[str] = "category",
        metrics_cols: Optional[List[str]] = None,
        output_path: str = "./reports",
        report_name: str = "model_comparison_report.html",
        artifact_path: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> str:
        """
        Generate an HTML report comparing two datasets of LLM responses.

        Args:
            reference_data: Reference dataset
            current_data: Current dataset
            response_col: Column containing the text responses
            category_col: Column containing response categories
            metrics_cols: Additional numerical columns to include in comparison
            output_path: Directory to save the report
            report_name: Filename for the HTML report
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            str: Path to the generated report
        """
        return self._monitor.generate_comparison_report(
            reference_data=reference_data,
            current_data=current_data,
            response_col=response_col,
            category_col=category_col,
            metrics_cols=metrics_cols,
            output_path=output_path,
            report_name=report_name,
            artifact_path=artifact_path,
            run_id=run_id,
        )

    # pylint: disable=too-many-arguments,too-many-locals
    def run_comprehensive_evaluation(
        self,
        data: pd.DataFrame,
        response_col: str = "response",
        prompt_col: Optional[str] = "prompt",
        reference_col: Optional[str] = None,
        categorical_cols: Optional[List[str]] = None,
        words_to_check: Optional[List[str]] = None,
        run_sentiment: bool = True,
        run_toxicity: bool = True,
        run_llm_judge: bool = False,
        reference_data: Optional[pd.DataFrame] = None,
        column_mapping: Optional[Any] = None,
        save_html: bool = False,
        output_path: str = "./reports",
        artifact_path: str = "llm_evaluation",
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a comprehensive evaluation of LLM responses.

        Args:
            data: Dataset with LLM responses
            response_col: Column name containing model responses
            prompt_col: Column name containing prompts/questions
            reference_col: Column name containing reference responses
            categorical_cols: List of categorical feature columns
            words_to_check: List of words to check for in responses
            run_sentiment: Whether to check sentiment
            run_toxicity: Whether to check toxicity
            run_llm_judge: Whether to run LLM-as-judge
            reference_data: Reference dataset for comparison
            column_mapping: Column mapping for the dataset
            save_html: Whether to save the report as HTML
            output_path: Directory to save report files
            artifact_path: MLflow artifact path for logging
            run_id: MLflow run ID

        Returns:
            Dict[str, Any]: Dictionary with all evaluation reports
        """
        # pylint: enable=too-many-arguments,too-many-locals
        return self._monitor.run_comprehensive_evaluation(
            data=data,
            response_col=response_col,
            prompt_col=prompt_col,
            reference_col=reference_col,
            categorical_cols=categorical_cols,
            words_to_check=words_to_check,
            run_sentiment=run_sentiment,
            run_toxicity=run_toxicity,
            run_llm_judge=run_llm_judge,
            reference_data=reference_data,
            column_mapping=column_mapping,
            save_html=save_html,
            output_path=output_path,
            artifact_path=artifact_path,
            run_id=run_id,
        )

    def log_metrics_to_mlflow(
        self, metrics: Union[Any, Dict[str, Any]], run_id: Optional[str] = None
    ) -> bool:
        """
        Log metrics to MLflow.

        Args:
            metrics: The metrics, report, or test suite to log
            run_id: MLflow run ID. If not provided, uses active run

        Returns:
            bool: True if metrics were successfully logged
        """
        return self._monitor.log_metrics_to_mlflow(metrics=metrics, run_id=run_id)

    # Expose the underlying monitor for advanced use cases
    @property
    def monitor(self):
        """Get the underlying monitor implementation."""
        return self._monitor

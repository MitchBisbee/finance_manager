"""A module for generating plotly plots
"""
import plotly.graph_objects as go


class PlotlyPlots:
    """Utility class for generating common Plotly chart types."""
    @staticmethod
    def pie_chart(data: dict):
        """
        Creates and returns a pie chart.

        Expected keys in data:
            - labels: list of category labels
            - values: list of corresponding numeric values
            - name (optional): trace name for the pie chart
        """
        labels = data.get("labels", [])
        values = data.get("values", [])
        name = data.get("name", "Pie Chart")

        fig = go.Figure(
            data=[go.Pie(labels=labels, values=values, name=name)]
        )
        return fig

    @staticmethod
    def scatter_plot(data: dict):
        """
        Creates and returns a scatter plot.

        Expected keys in data:
            - x: list of x-values
            - y: list of y-values
            - name (optional): trace name
        """
        x = data.get("x", [])
        y = data.get("y", [])
        name = data.get("name", "Scatter Plot")

        fig = go.Figure(
            data=[go.Scatter(x=x, y=y, mode="markers", name=name)]
        )
        return fig

    @staticmethod
    def bar_chart(data: dict):
        """
        Creates and returns a bar chart.

        Expected keys in data:
            - x: list of categories (x-axis)
            - y: list of values (heights)
            - name (optional): trace name
        """
        x = data.get("x", [])
        y = data.get("y", [])
        name = data.get("name", "Bar Chart")

        fig = go.Figure(
            data=[go.Bar(x=x, y=y, name=name)]
        )
        return fig

    @staticmethod
    def line_chart(data: dict):
        """
        Creates and returns a Plotly line chart.

        Expected keys in data:
            - x: list of x-values
            - y: list of y-values
            - name (optional): trace label
        """
        x = data.get("x", [])
        y = data.get("y", [])
        name = data.get("name", "Line")

        fig = go.Figure(
            data=[go.Scatter(x=x, y=y, mode="lines", name=name)]
        )
        return fig


if __name__ == "__main__":
    pass

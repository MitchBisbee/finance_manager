"""##  A module for generating plotly plots
"""
import plotly.graph_objects as go


class PlotlyPlots:
    """## A class for generating plotly plots.
    """

    def __init__(self, data):
        # Initialize with data
        self.data = data

    def pie_chart(self):
        """Creates and returns a pie chart."""
        fig = go.Figure(
            data=[go.Pie(labels=self.data["Labels"], values=self.data['Values'])])
        return fig

    def scatter_plot(self):
        """Creates and returns a scatter plot."""
        fig = go.Figure(
            data=[go.Scatter(x=self.data['Date'], y=self.data['Value'], mode='markers')])
        return fig

    def bar_chart(self):
        """Creates and returns a bar chart."""
        fig = go.Figure(
            data=[go.Bar(x=self.data['Date'], y=self.data['Value'])])
        return fig

    def line_chart(self):
        """Creates and returns a line chart."""
        fig = go.Figure(
            data=[go.Scatter(x=self.data['Date'], y=self.data['Value'], mode='lines')])
        return fig


if __name__ == "__main__":
    pass

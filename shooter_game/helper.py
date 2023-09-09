import plotly.express as px
import plotly.io as pio


def plot(scores, mean_scores):
        fig = px.line(x=scores) 
        fig.add_scatter(x=mean_scores)
        fig.show()

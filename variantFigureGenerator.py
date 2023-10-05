import subprocess
import svg

lineLen = 660-60
proteinLen = 564

bar1 = [
    svg.Rect(
            fill="gold",
            x=60+(1/proteinLen) * lineLen,
            y=185,
            width=(22/proteinLen) * lineLen,
            height=30,
            stroke="orange",
            stroke_width=3
        ),
        svg.Rect(
            fill="lime",
            x=60+(23/proteinLen) * lineLen + 3,
            y=185,
            width=(((51-23)/proteinLen) * lineLen) - 6,
            height=30,
            stroke="green",
            stroke_width=3
        ),
        svg.Rect(
            fill="red",
            x=60+(52/proteinLen) * lineLen + 3,
            y=185,
            width=(((299-52)/proteinLen) * lineLen) - 6,
            height=30,
            stroke="darkred",
            stroke_width=3
        ),
        svg.Rect(
            fill="lightblue",
            x=60+(311/proteinLen) * lineLen + 3,
            y=185,
            width=(((421-311)/proteinLen) * lineLen) - 6,
            height=30,
            stroke="blue",
            stroke_width=3
        ),
        svg.Rect(
            fill="lightblue",
            x=60+(431/proteinLen) * lineLen + 3,
            y=185,
            width=(((543-431)/proteinLen) * lineLen) - 6,
            height=30,
            stroke="blue",
            stroke_width=3
        ),
]

bar2 = [
    svg.Rect(
            fill="gold",
            x=60+(1/proteinLen) * lineLen,
            y=345,
            width=(22/proteinLen) * lineLen,
            height=30,
            stroke="orange",
            stroke_width=3
        ),
        svg.Rect(
            fill="lime",
            x=60+(23/proteinLen) * lineLen + 3,
            y=345,
            width=(((51-23)/proteinLen) * lineLen) - 6,
            height=30,
            stroke="green",
            stroke_width=3
        ),
        svg.Rect(
            fill="red",
            x=60+(52/proteinLen) * lineLen + 3,
            y=345,
            width=(((299-52)/proteinLen) * lineLen) - 6,
            height=30,
            stroke="darkred",
            stroke_width=3
        ),
        svg.Rect(
            fill="lightblue",
            x=60+(311/proteinLen) * lineLen + 3,
            y=345,
            width=(((421-311)/proteinLen) * lineLen) - 6,
            height=30,
            stroke="blue",
            stroke_width=3
        ),
        svg.Rect(
            fill="lightblue",
            x=60+(431/proteinLen) * lineLen + 3,
            y=345,
            width=(((543-431)/proteinLen) * lineLen) - 6,
            height=30,
            stroke="blue",
            stroke_width=3
        ),
]

canvas = svg.SVG(
    width=720,
    height=480,
    elements=[
        svg.Rect( # BACKGROUND
            fill="white",
            x=0,
            y=0,
            width=720,
            height=480
        ),
        svg.Line( # FIRST LINE
            stroke_width=5,
            stroke="grey",
            x1=60,
            y1=200,
            x2=660,
            y2=200
        ),
        svg.Line( # SECOND LINE
            stroke_width=5,
            stroke="grey",
            x1=60,
            y1=360,
            x2=660,
            y2=360
        ),
        svg.Text( # 0|1 TEXT
            text='0|1',
            x=15,
            y=205,
            stroke="black",
            font_family="Gill Sans",
            font_weight=1,
            font_size=20
        ),
        svg.Text( # 1|0 TEXT
            text='1|0',
            x=15,
            y=365,
            stroke="black",
            font_family="Gill Sans",
            font_weight=1,
            font_size=20
        ),
    ]+bar1+bar2,
)

svg_string = str(canvas)

with open('/mnt/shared_storage/webapp/polarPipeline/static/variantFig.svg', 'w') as opened:
    opened.write(svg_string)

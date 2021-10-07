from logging import debug
from os import name, stat
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

engine = create_engine("sqlite:///Resources/hawaii.sqlite?check_same_thread=False")
Base = automap_base()
Base.prepare(engine, reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement
session = Session(engine)

app = Flask(__name__)

@app.route('/')
def home():
    return (
        f'Welcome to the API!<br/>'
        f'Here are the available routes:<br/>'
        f'/api/v1.0/stations<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'/api/v1.0/tobs<br/>'
        f'/api/v1.0/date/<start><br/>'
        f'/api/v1.0/date/<start>/<end>'
    )

@app.route("/api/v1.0/stations")
def stations():
    stats = session.query(Station.station, Station.name).all()
    names = []
    for st, nm in stats:
        names.append({
            'Station':st,
            'Name':nm
        })

    return jsonify(names)

@app.route("/api/v1.0/precipitation")
def waterfall():
    strDate = session.query(func.max(Measurement.date)).first()[0]
    prevYear = dt.datetime.strptime(strDate, '%Y-%m-%d') - dt.timedelta(365)
    precip = session.query(Measurement.prcp, Measurement.date).filter(Measurement.date > prevYear).all()
    rains = []
    for pc, d in precip:
        rains.append({
            'Precipitation':pc,
            'Date':d
        })

    return jsonify(rains)

@app.route("/api/v1.0/tobs")
def tempurs():
    strDate = session.query(func.max(Measurement.date)).first()[0]
    prevYear = dt.datetime.strptime(strDate, '%Y-%m-%d') - dt.timedelta(365)
    temps = session.query(Measurement.tobs, Measurement.date).filter(Measurement.date > prevYear).all()
    heats = []
    for t, d in temps:
        heats.append({
            'Temperature':t,
            'Date':d
        })

    return jsonify(heats)

@app.route("/api/v1.0/date/<start>")
@app.route("/api/v1.0/date/<start>/<end>")
def stats(start=None, end=None):
    sd = [func.min(Measurement.tobs),
          func.max(Measurement.tobs),
          func.avg(Measurement.tobs)]
    if not end:
        results = session.query(*sd).filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
    else:
        results = session.query(*sd).filter(Measurement.date >= start, Measurement.date <= end).all()
        temps = list(np.ravel(results))
    temps.append(start)
    return jsonify(temps)

if __name__ == '__main__':
     app.run(debug=True)
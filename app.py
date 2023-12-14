# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, text, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurements = Base.classes.measurement
stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """Module 10 Challenge: SQLAlchemy and Flask"""

    """List of all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query results from precipitation analysis (last 12 months of data)"""
    
   # Starting from the most recent data point in the database. 
    most_rec_date = session.query(measurements.date).order_by(measurements.date.desc()).first().date

    # Calculate the date one year from the last date in data set.
    rec_twelve_months = dt.datetime.strptime(most_rec_date, '%Y-%m-%d') - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    sel = [measurements.date,measurements.prcp]

    year_results = session.query(*sel).filter(measurements.date >= rec_twelve_months).filter(measurements.station == 'USC00519281').all()
    
    session.close()

    # Convert list of tuples into normal list
    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in year_results}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query results showing all station names"""

    # Perform a query to retrieve all station names
    station_names = session.query(measurements.station).group_by(measurements.station).all()
    
    #end session
    session.close()

    # Convert list of tuples into normal list
    station_names_list = list(np.ravel(station_names))

    return jsonify(station_names_list)

@app.route("/api/v1.0/tobs")
def temps():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Query results for last 12 months at most active station"""

    # Starting from the most recent data point in the database. 
    most_rec_date = session.query(measurements.date).order_by(measurements.date.desc()).first().date

    # Calculate the date one year from the last date in data set.
    rec_twelve_months = dt.datetime.strptime(most_rec_date, '%Y-%m-%d') - dt.timedelta(days=366)
    
    # Using the most active station id
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    temp_results = session.query(measurements.date,measurements.tobs).filter(measurements.date >= rec_twelve_months).\
               filter(measurements.station == 'USC00519281').all()

    #end session
    session.close()

    # Convert list of tuples into normal list
    temp_results_list = list(np.ravel(temp_results))

    return jsonify(temp_results_list)


@app.route("/api/v1.0/<start>")
def temp_data_start_date(start):
    """Fetch dates and temperature observations from variable start date"""

    # Perform a query to retrieve the data and precipitation scores
    sel_stats = [func.min(measurements.tobs),func.max(measurements.tobs),func.avg(measurements.tobs)]
    start_date_results = session.query(*sel_stats).filter(measurements.date >= start).all()

    session.close()

    # Convert list of tuples into normal list
    start_date_results_list = list(np.ravel(start_date_results))

    return jsonify(start_date_results_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_data_start_end_date(start,end):
    """Fetch dates and temperature observations from variable start date and end date"""

    # Perform a query to retrieve the data and precipitation scores
    sel_stats = [func.min(measurements.tobs),func.max(measurements.tobs),func.avg(measurements.tobs)]

    start_date_results = session.query(*sel_stats).filter(measurements.date >= start).filter(measurements.date <= end).all()

    session.close()

    # Convert list of tuples into normal list
    start_date_results_list = list(np.ravel(start_date_results))

    return jsonify(start_date_results_list)


if __name__ == '__main__':
    app.run(debug=True)
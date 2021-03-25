import pandas as pd
import plotly.graph_objs as go
import plotly.colors
import numpy as np
import requests
from collections import OrderedDict

# create a list of countries of interest
# we need an ordered dict because the API takes in ISO-3 codes, and using the ordered dictionary will plot countries in the same
# order in each graph, keeping country color consistency
country_default = OrderedDict([('Canada', 'CAN'), ('United States', 'USA'), ('Brazil', 'BRA'), ('France', 'FRA'), ('India', 'IND'),
                              ('Italy', 'ITA'), ('Germany', 'DEU'), ('United Kingdom', 'GBR'), ('China', 'CHN'), ('Japan', 'JPN'),
                              ('Russia', 'RUS'), ('Turkmenistan', 'TKM')])

# , ('Turkmenistan', 'TKM')

def return_figures(countries = country_default):
    """Creates plotly visualizations
    
    # Example of the World Bank API endpoint:
    # arable land for the United States and Brazil from 1990 to 2015
    # http://api.worldbank.org/v2/countries/usa;bra/indicators/AG.LND.ARBL.HA?date=1990:2015&per_page=1000&format=json

    Args:
        country_default (dict): list of countries for filtering the data

    Returns:
        list (dict): list containing the four plotly visualizations

    """
    
    # when the countries variable is empty, use the country_default dictionary
    if not bool(countries):
        countries = country_default
        
    # prepare filter data for World Bank API
    # the API uses ISO-3 country codes separated by ;
    country_filter = list(countries.values())
    country_filter = [x.lower() for x in country_filter]
    country_filter = ';'.join(country_filter)
    
    # World Bank indicators of interest for pulling data
    indicators = ['AG.LND.ARBL.HA.PC', 'SP.RUR.TOTL.ZS', 'SP.RUR.TOTL.ZS', 'AG.LND.FRST.ZS']

    # empty lists to store DataFrames with indicators of interest
    data_frames = []
    # and url endpoints of the World Bank API
    urls = []
    
    # pull data from World Bank API and clean the resulting json
    # results stored in data_frames variable
    for indicator in indicators:
      url = 'http://api.worldbank.org/v2/countries/' + country_filter +\
      '/indicators/' + indicator + '?date=1992:2018&per_page=1000&format=json'
      urls.append(url)

      try:
        r = requests.get(url)
        data = r.json()[1]
      except:
        print('could not load data ', indicator)

      for i, value in enumerate(data):
        value['indicator'] = value['indicator']['value']
        value['country'] = value['country']['value']

      data_frames.append(data)
    
    # first chart plots arable land from 1992 to 2018 as a line chart
    graph_one = []
    
    df_one = pd.DataFrame(data_frames[0])
    
    # filter and sort values for the visualization
    # filtering plots the countries in decreasing order by their values
    #df_one = df_one[(df_one['date'] == '2018') | (df_one['date'] == '1992')]
    #df_one.sort_values('value', ascending=False, inplace=True)
    
    # create a list of countries to use with all charts
    countrylist = df_one.country.unique().tolist()
    
    # add values to the plotly graph object
    for country in countrylist:
        x_val = df_one[df_one.country == country].date.tolist()
        y_val = df_one[df_one.country == country].value.tolist()
        graph_one.append(
            go.Scatter(
                x = x_val,
                y = y_val,
                mode = 'lines',
                name = country)
        )

    layout_one = dict(title = 'Change in Arable Land<br>1992 to 2018',
                xaxis = dict(title = 'Year', autoticks = True, tick0 = 1992),
                yaxis = dict(title = 'Hectares / person'),
                )

    # second chart plots ararble land for 2018 as a bar chart    
    graph_two = []
    
    df_one.sort_values('value', ascending = False, inplace = True)
    df_one = df_one[df_one.date == '2018']

    graph_two.append(
        go.Bar(
            x = df_one.country.tolist(),
            y = df_one.value.tolist(),
        )
    )

    layout_two = dict(title = 'Arable Land in 2018',
                xaxis = dict(title = 'Country',),
                yaxis = dict(title = 'Hectares / person'),
                )


    # third chart plots percent of population that is rural from 1992 to 2018
    graph_three = []
    
    df_three = pd.DataFrame(data_frames[1])
    #df_three = df_three[(df_three['date'] == '2018') | (df_three['date'] == '1992')]
    #df_three.sort_values('value', ascending = False, inplace = True)
    
    for country in countrylist:
        x_val = df_three[df_three.country == country].date.tolist()
        y_val = df_three[df_three.country == country].value.tolist()
        graph_three.append(
            go.Scatter(
                x = x_val,
                y = y_val,
                mode = 'lines',
                name = country
      )
    )

    layout_three = dict(title = 'Change in Rural Population<br>1992-2018',
                xaxis = dict(title = 'Year', autotick = True, tick0 = 1992),
                yaxis = dict(title = 'Percent')
                       )
    
    # fourth chart shows rural population vs arable land
    graph_four = []
    
    df_four_a = pd.DataFrame(data_frames[2])
    df_four_a = df_four_a[['country', 'date', 'value']]
    
    df_four_b = pd.DataFrame(data_frames[3])
    df_four_b = df_four_b[['country', 'date', 'value']]
    
    df_four = df_four_a.merge(df_four_b, on = ['country', 'date'])
    df_four.sort_values('date', ascending = True, inplace = True)
    
    #plotly_default_colors = plotly.colors.DEFAULT_PLOTLY_COLORS
    
    for country in countrylist:
        
        current_color = []
        
        x_val = df_four[df_four.country == country].value_x.tolist()
        y_val = df_four[df_four.country == country].value_y.tolist()
        years = df_four[df_four.country == country].date.tolist()
        country_label = df_four[df_four.country == country].country.tolist()
        
        text = []
        
        for country, year in zip(country_label, years):
            text.append(str(country) + ' ' + str(year))
            
        graph_four.append(
            go.Scatter(
                x = x_val,
                y = y_val,
                mode = 'lines+markers',
                text = text,
                name = country,
                textposition = 'top'
            )
        )
    
    
    layout_four = dict(title = 'Rural population vs. Forested Land<br>1992-2018',
                xaxis = dict(title = 'Rural pop. (% of total)', range = [0,100], dtick = 10),
                yaxis = dict(title = 'Forested Land (% of total)', range = [0,100], dtick = 10),
                )
    
    # append all charts to the figures list
    figures = []
    figures.append(dict(data=graph_one, layout=layout_one))
    figures.append(dict(data=graph_two, layout=layout_two))
    figures.append(dict(data=graph_three, layout=layout_three))
    figures.append(dict(data=graph_four, layout=layout_four))

    return figures
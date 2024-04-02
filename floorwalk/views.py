from django.db.models import Count
from django.shortcuts import render
import pandas as pd

from research_floorwalk.settings import BASE_DIR
from .models import *
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import Coalesce
from django.db.models import Count
from plotly.offline import plot
import plotly.graph_objs as go
#from django.contrib.staticfiles import finders
from research_floorwalk.settings import BASE_DIR
import os
# Create your views here.

def sitemap(request):
    #xml_file_path = finders.find('sitemap.xml')
    xml_file_path = os.path.join(BASE_DIR, 'static', 'sitemap', 'sitemap.xml')
    if xml_file_path:
        with open(xml_file_path, 'r') as xml_file:
            xml_content = xml_file.read()
        return render(request, 'sitemap.html', {'xml_content': xml_content})
    else:
        # Handle file not found error
        return render(request, 'index.html')
    
def index(request):
    return render(request, 'index.html')

def search_results(request):
    if request.method == 'GET':

        selected_industry = request.GET.get('industries')
        selected_state = request.GET.getlist('states')
        selected_brand = request.GET.getlist('brands')

        if selected_industry == 'Apparel':
            industry = 'Apparel'
            if selected_state:
                if selected_brand:

                    all_states = set(Apparel.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Apparel.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        
                        state_data.append(state_row)
                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits
                        
                    queryset = Apparel.objects.filter(state__in=selected_state, brand_name__in=selected_brand)
                    
                    # Use annotate and values to group by city and count the number of stores
                    city_counts = queryset.values('state', 'city').annotate(store_count=Count('store_name'))

                    # Order the results in descending order of store_count
                    sorted_city_counts = city_counts.order_by('-state', '-store_count')

                    # Display only the top 5 cities for each state
                    state_grouped_cities = {}
                    for city_data in sorted_city_counts:
                        state = city_data['state']
                        city = city_data['city']
                        store_count = city_data['store_count']

                        if state not in state_grouped_cities:
                            state_grouped_cities[state] = {'count': 0, 'cities': []}

                        if state_grouped_cities[state]['count'] < 5:
                            state_grouped_cities[state]['cities'].append({'city': city, 'store_count': store_count})
                            state_grouped_cities[state]['count'] += 1

                    result_dict = {}
                    data = []
                    # Loop through each state in the state_list
                    for state in selected_state:
                        # Filter data based on the current state and brand list
                        filtered_data = Apparel.objects.filter(state=state, brand_name__in=selected_brand)
                        
                        # Aggregate the count of stores for each brand
                        brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                        #graph
                        store_counts = Apparel.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]

                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)

                        # Create a dictionary to store the counts for the current state
                        state_counts_dict = {}
                        
                        # Populate the dictionary with brand counts
                        for entry in brand_counts:
                            state_counts_dict[entry['brand_name']] = entry['store_count']
                        
                        # Fill in 0 for brands with no stores
                        for brand in selected_brand:
                            if brand not in state_counts_dict:
                                state_counts_dict[brand] = 0
                        
                        # Add the state counts dictionary to the result_dict
                        result_dict[state] = state_counts_dict
                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')

                    selected_brand.sort()
                    for state in result_dict:
                        # Sort the state_counts_dict based on selected_brand order
                        sorted_state_counts = {brand: result_dict[state].get(brand, 0) for brand in selected_brand}
                        
                        # Update the result_dict with the sorted state_counts_dict
                        result_dict[state] = sorted_state_counts
                    
                    context = {
                    'industry': industry,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand,
                    'top_cities': top_cities,
                    'state_grouped_cities': state_grouped_cities,
                    'graph': graph,
                    'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                
                else:
                    all_states = set(Apparel.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Apparel.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        state_data.append(state_row)
                    
                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits

                    brand_counts = {}

                    # Get a set of all unique brand names
                    all_brands = set(Apparel.objects.values_list('brand_name', flat=True))
                    all_brands = sorted(list(all_brands))
                    data = []
                    for state in selected_state:
                        brand_counts[state] = {}
                        store_counts = Apparel.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]
                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)
                        # Query to get the count of stores for each brand in the given state
                        stores_count = (
                            Apparel.objects
                            .filter(state=state)
                            .values('brand_name')
                            .annotate(store_count=Count('store_name'))
                        )

                        # Populate the brand_counts dictionary
                        for brand in all_brands:
                            # If the brand is present in the stores_count result, use its count; otherwise, set it to 0
                            brand_count = next((entry['store_count'] for entry in stores_count if entry['brand_name'] == brand), 0)
                            brand_counts[state][brand] = brand_count

                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')
                    
                    context = {
                        'industry': industry,
                        'brand_counts': brand_counts,
                        'all_brands': all_brands,
                        'selected_state': selected_state,
                        'selected_brand': selected_brand,
                        'top_cities': top_cities,
                        'graph': graph,
                        'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
            
            elif selected_brand:

                result_dict = {}

                # Get distinct states from the database
                distinct_states = Apparel.objects.values('state').distinct()
                distinct_states = sorted(distinct_states, key=lambda x: x['state'])
                data = []
                state_data = []
                # Iterate through each state
                for state_info in distinct_states:
                    state_name = state_info['state']
                    state_row = {'state': state_name}
                    # Filter the data for the current state
                    state_whole_data = Apparel.objects.filter(state=state_name)

                    #graph
                    store_counts = Apparel.objects.filter(state=state_name, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                    if len(store_counts) == 0:
                        store_counts = [{'state': state_name, 'store_count': 0}]
                        state_row['store_counts'] = 0
                    else:
                        state_row['store_counts'] = store_counts[0]['store_count']
                    state_data.append(state_row)
                    # bar_colors = ['blue', 'green', 'orange', 'red', 'purple']
                    state_graph_data = {
                        'x': [state_name],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state_name,
                        # 'marker': {'color': bar_colors}
                    }
                    data.append(state_graph_data)
                    # Create a sub-dictionary for the current state
                    state_dict = {}
                    
                    # Iterate through selected brands
                    for brand_name in selected_brand:
                        # Count the number of stores for the current brand in the current state
                        store_count = state_whole_data.filter(brand_name=brand_name).count()
                        
                        # Add the brand count to the sub-dictionary
                        state_dict[brand_name] = store_count

                    # Add the sub-dictionary to the result dictionary
                    result_dict[state_name] = state_dict

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'},
                    
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')
                
                context = {
                    'industry': industry,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'graph': graph,
                    'state_data': state_data
                }
                return render(request, 'filter.html',context)
            
            else:
                result = (
                    Apparel.objects
                    .values('state', 'brand_name')
                    .annotate(count=Coalesce(Count('store_name'), 0))
                )

                # Create a dictionary to store the result with default values set to 0
                state_brand_counts = {}

                # Populate the dictionary with the query result
                for entry in result:
                    state = entry['state']
                    brand_name = entry['brand_name']
                    count = entry['count']

                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    state_brand_counts[state][brand_name] = count

                # Add entries with count 0 for any missing combinations
                all_states = set(Apparel.objects.values_list('state', flat=True).distinct())
                all_brands = set(Apparel.objects.values_list('brand_name', flat=True).distinct())
                # print(sorted(all_states))
                # print(sorted(all_brands))
                all_brands = sorted(list(all_brands))
                for state in all_states:
                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    for brand_name in all_brands:
                        if brand_name not in state_brand_counts[state]:
                            state_brand_counts[state][brand_name] = 0


                state_data = []
                data = []
                for state in all_states:
                    state_row = {'state': state}
                    
                    # Fetch state census data
                    state_census_data = State_census.objects.filter(state_name=state).first()
                    population = None
                    if state_census_data:
                        state_row['total_population'] = round(state_census_data.total_population /  100000 , 2) 
                        population = state_census_data.total_population
                    else:
                        state_row['total_population'] = 0
                    
                    # Fetch store counts
                    queryset = Apparel.objects.filter(state=state)
                    store_counts = queryset.values('state').annotate(store_count=Count('store_name'))


                    state_graph_data = {
                        'x': [state],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state
                    }
                    data.append(state_graph_data)
                    
                    if store_counts:
                        state_row['store_counts'] = store_counts[0]['store_count']
                        # Calculate ratio
                        if population is not None:
                            state_row['ratio'] =round ( (state_row['store_counts'] / population ) * 10000, 2 )
                        else:
                            state_row['ratio'] = 0
                    else:
                        state_row['store_counts'] = 0
                        state_row['ratio'] = 0

                    state_data.append(state_row)

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'}
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')

                rows = []
                for state, brand_counts in state_brand_counts.items():
                    
                    row = {'state': state}
                    for brand in all_brands:
                        row[brand] = brand_counts.get(brand, 0)
                    rows.append(row)
                headers = rows[0].keys()
                
                table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)
                rows = sorted(rows, key=lambda x: x['state'])
                state_data = sorted(state_data, key=lambda x: x['state'])

                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    # 'table': html_table,
                    'state_data': state_data,
                    'graph': graph,
                    'headers':headers, 
                    'table_data':table_data,
                    'industry': industry,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand
                }
                
                return render(request, 'filter.html', context)
        
        elif selected_industry == 'Automobile':
            industry = 'Automobile'
            if selected_state:
                if selected_brand:

                    all_states = set(Automobile.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Automobile.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        
                        state_data.append(state_row)
                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits
                        
                    queryset = Automobile.objects.filter(state__in=selected_state, brand_name__in=selected_brand)
                    
                    # Use annotate and values to group by city and count the number of stores
                    city_counts = queryset.values('state', 'city').annotate(store_count=Count('store_name'))

                    # Order the results in descending order of store_count
                    sorted_city_counts = city_counts.order_by('-state', '-store_count')

                    # Display only the top 5 cities for each state
                    state_grouped_cities = {}
                    for city_data in sorted_city_counts:
                        state = city_data['state']
                        city = city_data['city']
                        store_count = city_data['store_count']

                        if state not in state_grouped_cities:
                            state_grouped_cities[state] = {'count': 0, 'cities': []}

                        if state_grouped_cities[state]['count'] < 5:
                            state_grouped_cities[state]['cities'].append({'city': city, 'store_count': store_count})
                            state_grouped_cities[state]['count'] += 1

                    result_dict = {}
                    data = []
                    # Loop through each state in the state_list
                    for state in selected_state:
                        # Filter data based on the current state and brand list
                        filtered_data = Automobile.objects.filter(state=state, brand_name__in=selected_brand)
                        
                        # Aggregate the count of stores for each brand
                        brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                        #graph
                        store_counts = Automobile.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]

                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)

                        # Create a dictionary to store the counts for the current state
                        state_counts_dict = {}
                        
                        # Populate the dictionary with brand counts
                        for entry in brand_counts:
                            state_counts_dict[entry['brand_name']] = entry['store_count']
                        
                        # Fill in 0 for brands with no stores
                        for brand in selected_brand:
                            if brand not in state_counts_dict:
                                state_counts_dict[brand] = 0
                        
                        # Add the state counts dictionary to the result_dict
                        result_dict[state] = state_counts_dict
                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')

                    selected_brand.sort()
                    for state in result_dict:
                        # Sort the state_counts_dict based on selected_brand order
                        sorted_state_counts = {brand: result_dict[state].get(brand, 0) for brand in selected_brand}
                        
                        # Update the result_dict with the sorted state_counts_dict
                        result_dict[state] = sorted_state_counts
                    
                    context = {
                    'industry': industry,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand,
                    'top_cities': top_cities,
                    'state_grouped_cities': state_grouped_cities,
                    'graph': graph,
                    'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                
                else:
                    # result = (
                    #     Automobile.objects.values('brand_name', 'state')
                    #     .annotate(store_count=Count('id'))
                    #     .filter(state__in=selected_state)
                    #     .order_by('brand_name', 'state')
                    # )

                    # # Create a dictionary to store the results
                    # brand_state_counts = {}

                    # # Initialize the dictionary with all brands and states
                    # for brand in set(result.values_list('brand_name', flat=True)):
                    #     brand_state_counts[brand] = {state: 0 for state in selected_state}

                    # # Populate the dictionary with the actual counts
                    # for entry in result:
                    #     brand_state_counts[entry['brand_name']][entry['state']] = entry['store_count']
                    
                    # print(brand_state_counts)
                    all_states = set(Automobile.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Automobile.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        state_data.append(state_row)
                    
                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits

                    brand_counts = {}

                    # Get a set of all unique brand names
                    all_brands = set(Automobile.objects.values_list('brand_name', flat=True))
                    all_brands = sorted(list(all_brands))
                    data = []
                    for state in selected_state:
                        brand_counts[state] = {}
                        store_counts = Automobile.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]
                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)
                        # Query to get the count of stores for each brand in the given state
                        stores_count = (
                            Automobile.objects
                            .filter(state=state)
                            .values('brand_name')
                            .annotate(store_count=Count('store_name'))
                        )

                        # Populate the brand_counts dictionary
                        for brand in all_brands:
                            # If the brand is present in the stores_count result, use its count; otherwise, set it to 0
                            brand_count = next((entry['store_count'] for entry in stores_count if entry['brand_name'] == brand), 0)
                            brand_counts[state][brand] = brand_count

                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')
                    
                    context = {
                        'industry': industry,
                        'brand_counts': brand_counts,
                        'all_brands': all_brands,
                        'selected_state': selected_state,
                        'selected_brand': selected_brand,
                        'top_cities': top_cities,
                        'graph': graph,
                        'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                    
            elif selected_brand:

                result_dict = {}

                # Get distinct states from the database
                distinct_states = Automobile.objects.values('state').distinct()
                distinct_states = sorted(distinct_states, key=lambda x: x['state'])
                data = []
                state_data = []
                # Iterate through each state
                for state_info in distinct_states:
                    state_name = state_info['state']
                    state_row = {'state': state_name}
                    # Filter the data for the current state
                    state_whole_data = Automobile.objects.filter(state=state_name)

                    #graph
                    store_counts = Automobile.objects.filter(state=state_name, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                    if len(store_counts) == 0:
                        store_counts = [{'state': state_name, 'store_count': 0}]
                        state_row['store_counts'] = 0
                    else:
                        state_row['store_counts'] = store_counts[0]['store_count']
                    state_data.append(state_row)
                    # bar_colors = ['blue', 'green', 'orange', 'red', 'purple']
                    state_graph_data = {
                        'x': [state_name],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state_name,
                        # 'marker': {'color': bar_colors}
                    }
                    data.append(state_graph_data)
                    # Create a sub-dictionary for the current state
                    state_dict = {}
                    
                    # Iterate through selected brands
                    for brand_name in selected_brand:
                        # Count the number of stores for the current brand in the current state
                        store_count = state_whole_data.filter(brand_name=brand_name).count()
                        
                        # Add the brand count to the sub-dictionary
                        state_dict[brand_name] = store_count

                    # Add the sub-dictionary to the result dictionary
                    result_dict[state_name] = state_dict

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'},
                    
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')
                
                context = {
                    'industry': industry,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'graph': graph,
                    'state_data': state_data
                }
                return render(request, 'filter.html',context)
            
            else:
                # unique_states = set(Automobile.objects.values_list('state', flat=True).distinct())
                # unique_brands = set(Automobile.objects.values_list('brand_name', flat=True).distinct())
                # state_brand_mapping = {}
                # for state in unique_states:
                #     brand_counts_in_state = (
                #         Automobile.objects
                #         .filter(state=state)
                #         .values('brand_name')
                #         .annotate(store_count=Count('brand_name'))
                #     )
                #     state_brand_mapping[state] = [
                #         {'brand': item['brand_name'], 'store_count': item['store_count']}
                #         for item in brand_counts_in_state
                #     ]
             
                # context ={
                #     'industry': industry,
                #     'unique_states': unique_states,
                #     'state_brand_mapping': state_brand_mapping,
                #     'unique_brands': unique_brands
                # }
                
                result = (
                    Automobile.objects
                    .values('state', 'brand_name')
                    .annotate(count=Coalesce(Count('store_name'), 0))
                )

                # Create a dictionary to store the result with default values set to 0
                state_brand_counts = {}

                # Populate the dictionary with the query result
                for entry in result:
                    state = entry['state']
                    brand_name = entry['brand_name']
                    count = entry['count']

                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    state_brand_counts[state][brand_name] = count

                # Add entries with count 0 for any missing combinations
                all_states = set(Automobile.objects.values_list('state', flat=True).distinct())
                all_brands = set(Automobile.objects.values_list('brand_name', flat=True).distinct())
                # print(sorted(all_states))
                # print(sorted(all_brands))
                all_brands = sorted(list(all_brands))
                for state in all_states:
                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    for brand_name in all_brands:
                        if brand_name not in state_brand_counts[state]:
                            state_brand_counts[state][brand_name] = 0


                state_data = []
                data = []
                for state in all_states:
                    state_row = {'state': state}
                    
                    # Fetch state census data
                    state_census_data = State_census.objects.filter(state_name=state).first()
                    population = None
                    if state_census_data:
                        state_row['total_population'] = round(state_census_data.total_population /  100000 , 2) 
                        population = state_census_data.total_population
                    else:
                        state_row['total_population'] = 0
                    
                    # Fetch store counts
                    queryset = Automobile.objects.filter(state=state)
                    store_counts = queryset.values('state').annotate(store_count=Count('store_name'))


                    state_graph_data = {
                        'x': [state],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state
                    }
                    data.append(state_graph_data)
                    
                    if store_counts:
                        state_row['store_counts'] = store_counts[0]['store_count']
                        # Calculate ratio
                        if population is not None:
                            state_row['ratio'] = round ( (state_row['store_counts'] / population ) * 10000, 2 )
                        else:
                            state_row['ratio'] = 0
                    else:
                        state_row['store_counts'] = 0
                        state_row['ratio'] = 0

                    state_data.append(state_row)

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'}
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')

                rows = []
                for state, brand_counts in state_brand_counts.items():
                    
                    row = {'state': state}
                    for brand in all_brands:
                        row[brand] = brand_counts.get(brand, 0)
                    rows.append(row)
                headers = rows[0].keys()
                
                table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)
                rows = sorted(rows, key=lambda x: x['state'])
                state_data = sorted(state_data, key=lambda x: x['state'])

                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    # 'table': html_table,
                    'state_data': state_data,
                    'graph': graph,
                    'headers':headers, 
                    'table_data':table_data,
                    'industry': industry,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand
                }
                
                return render(request, 'filter.html', context)
        
        elif selected_industry == 'Electronic':
            industry = 'Electronic'
            if selected_state:
                if selected_brand:

                    
                    all_states = set(Electronic.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Electronic.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        
                        state_data.append(state_row)

                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits

                    queryset = Electronic.objects.filter(state__in=selected_state, brand_name__in=selected_brand)
                    
                    # Use annotate and values to group by city and count the number of stores
                    city_counts = queryset.values('state', 'city').annotate(store_count=Count('store_name'))

                    # Order the results in descending order of store_count
                    sorted_city_counts = city_counts.order_by('-state', '-store_count')

                    # Display only the top 5 cities for each state
                    state_grouped_cities = {}
                    for city_data in sorted_city_counts:
                        state = city_data['state']
                        city = city_data['city']
                        store_count = city_data['store_count']

                        if state not in state_grouped_cities:
                            state_grouped_cities[state] = {'count': 0, 'cities': []}

                        if state_grouped_cities[state]['count'] < 5:
                            state_grouped_cities[state]['cities'].append({'city': city, 'store_count': store_count})
                            state_grouped_cities[state]['count'] += 1


                    result_dict = {}
                    data = []

                    # Loop through each state in the state_list
                    for state in selected_state:
                        # Filter data based on the current state and brand list
                        filtered_data = Electronic.objects.filter(state=state, brand_name__in=selected_brand)
                        
                        # Aggregate the count of stores for each brand
                        brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                        
                        #graph
                        store_counts = Electronic.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]
                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)

                        # Create a dictionary to store the counts for the current state
                        state_counts_dict = {}
                        
                        # Populate the dictionary with brand counts
                        for entry in brand_counts:
                            state_counts_dict[entry['brand_name']] = entry['store_count']
                        
                        # Fill in 0 for brands with no stores
                        for brand in selected_brand:
                            if brand not in state_counts_dict:
                                state_counts_dict[brand] = 0
                        
                        # Add the state counts dictionary to the result_dict
                        result_dict[state] = state_counts_dict
                    
                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')

                    selected_brand.sort()
                    for state in result_dict:
                        # Sort the state_counts_dict based on selected_brand order
                        sorted_state_counts = {brand: result_dict[state].get(brand, 0) for brand in selected_brand}
                        
                        # Update the result_dict with the sorted state_counts_dict
                        result_dict[state] = sorted_state_counts
                    context = {
                    'industry': industry,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand,
                    'top_cities': top_cities,
                    'state_grouped_cities': state_grouped_cities,
                    'graph': graph,
                    'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                
                else:

                    all_states = set(Electronic.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Electronic.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        state_data.append(state_row)

                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits

                    brand_counts = {}

                    # Get a set of all unique brand names
                    all_brands = set(Electronic.objects.values_list('brand_name', flat=True))
                    all_brands = sorted(list(all_brands))
                    data = []
                    for state in selected_state:
                        brand_counts[state] = {}
                        store_counts = Electronic.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]
                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)

                        # Query to get the count of stores for each brand in the given state
                        stores_count = (
                            Electronic.objects
                            .filter(state=state)
                            .values('brand_name')
                            .annotate(store_count=Count('store_name'))
                        )

                        # Populate the brand_counts dictionary
                        for brand in all_brands:
                            # If the brand is present in the stores_count result, use its count; otherwise, set it to 0
                            brand_count = next((entry['store_count'] for entry in stores_count if entry['brand_name'] == brand), 0)
                            brand_counts[state][brand] = brand_count
                    
                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')

                    context = {
                        'industry': industry,
                        'brand_counts': brand_counts,
                        'all_brands': all_brands,
                        'selected_state': selected_state,
                        'selected_brand': selected_brand,
                        'top_cities': top_cities,
                        'graph': graph,
                        'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                    
            elif selected_brand:
                result_dict = {}

                # Get distinct states from the database
                distinct_states = Electronic.objects.values('state').distinct()
                distinct_states = sorted(distinct_states, key=lambda x: x['state'])
                data = []
                state_data = []

                # Iterate through each state
                for state_info in distinct_states:
                    state_name = state_info['state']
                    state_row = {'state': state_name}
                    # Filter the data for the current state
                    state_whole_data = Electronic.objects.filter(state=state_name)

                    #graph
                    store_counts = Electronic.objects.filter(state=state_name, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                    if len(store_counts) == 0:
                        store_counts = [{'state': state_name, 'store_count': 0}]
                        state_row['store_counts'] = 0
                    else:
                        state_row['store_counts'] = store_counts[0]['store_count']
                    state_data.append(state_row)
                    state_graph_data = {
                        'x': [state_name],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state_name
                    }
                    data.append(state_graph_data)

                    # Create a sub-dictionary for the current state
                    state_dict = {}

                    # Iterate through selected brands
                    for brand_name in selected_brand:
                        # Count the number of stores for the current brand in the current state
                        store_count = state_whole_data.filter(brand_name=brand_name).count()

                        # Add the brand count to the sub-dictionary
                        state_dict[brand_name] = store_count

                    # Add the sub-dictionary to the result dictionary
                    result_dict[state_name] = state_dict

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'}
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')

                context = {
                    'industry': industry,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'graph': graph,
                    'state_data': state_data
                }
                return render(request, 'filter.html',context)
            
            else:
                result = (
                    Electronic.objects
                    .values('state', 'brand_name')
                    .annotate(count=Coalesce(Count('store_name'), 0))
                )

                # Create a dictionary to store the result with default values set to 0
                state_brand_counts = {}

                # Populate the dictionary with the query result
                for entry in result:
                    state = entry['state']
                    brand_name = entry['brand_name']
                    count = entry['count']

                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    state_brand_counts[state][brand_name] = count

                # Add entries with count 0 for any missing combinations
                all_states = set(Electronic.objects.values_list('state', flat=True).distinct())
                all_brands = set(Electronic.objects.values_list('brand_name', flat=True).distinct())
                # print(sorted(all_states))
                # print(sorted(all_brands))
                all_brands = sorted(list(all_brands))

                for state in all_states:
                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    for brand_name in all_brands:
                        if brand_name not in state_brand_counts[state]:
                            state_brand_counts[state][brand_name] = 0


                state_data = []
                data = []
                for state in all_states:
                    state_row = {'state': state}
                    
                    # Fetch state census data
                    state_census_data = State_census.objects.filter(state_name=state).first()
                    population = None
                    if state_census_data:
                        state_row['total_population'] = round(state_census_data.total_population /  100000 , 2) 
                        population = state_census_data.total_population
                    else:
                        state_row['total_population'] = 0
                    
                    # Fetch store counts
                    queryset = Electronic.objects.filter(state=state)
                    store_counts = queryset.values('state').annotate(store_count=Count('store_name'))


                    state_graph_data = {
                        'x': [state],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state
                    }
                    data.append(state_graph_data)
                    
                    if store_counts:
                        state_row['store_counts'] = store_counts[0]['store_count']
                        # Calculate ratio
                        if population is not None:
                            state_row['ratio'] = round ( (state_row['store_counts'] / population ) * 10000, 2 )
                        else:
                            state_row['ratio'] = 0
                    else:
                        state_row['store_counts'] = 0
                        state_row['ratio'] = 0

                    state_data.append(state_row)

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'}
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')

                rows = []
                for state, brand_counts in state_brand_counts.items():
                    row = {'state': state}
                    for brand in all_brands:
                        row[brand] = brand_counts.get(brand, 0)
                    rows.append(row)
                headers = rows[0].keys()
                table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)
                
                rows = sorted(rows, key=lambda x: x['state'])
                state_data = sorted(state_data, key=lambda x: x['state'])

                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    # 'table': html_table,
                    'state_data': state_data,
                    'graph': graph,
                    'headers':headers, 
                    'table_data':table_data,
                    'industry': industry,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand
                }
                
                return render(request, 'filter.html', context)
           
        elif selected_industry == 'Entertainment':
            industry = 'Entertainment'
            if selected_state:
                if selected_brand:

                    all_states = set(Entertainment.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Entertainment.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        
                        state_data.append(state_row)

                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits

                    queryset = Entertainment.objects.filter(state__in=selected_state, brand_name__in=selected_brand)
                    
                    # Use annotate and values to group by city and count the number of stores
                    city_counts = queryset.values('state', 'city').annotate(store_count=Count('store_name'))

                    # Order the results in descending order of store_count
                    sorted_city_counts = city_counts.order_by('-state', '-store_count')

                    # Display only the top 5 cities for each state
                    state_grouped_cities = {}
                    for city_data in sorted_city_counts:
                        state = city_data['state']
                        city = city_data['city']
                        store_count = city_data['store_count']

                        if state not in state_grouped_cities:
                            state_grouped_cities[state] = {'count': 0, 'cities': []}

                        if state_grouped_cities[state]['count'] < 5:
                            state_grouped_cities[state]['cities'].append({'city': city, 'store_count': store_count})
                            state_grouped_cities[state]['count'] += 1


                    result_dict = {}
                    data = []

                    # Loop through each state in the state_list
                    for state in selected_state:
                        # Filter data based on the current state and brand list
                        filtered_data = Entertainment.objects.filter(state=state, brand_name__in=selected_brand)
                        
                        # Aggregate the count of stores for each brand
                        brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                        
                        #graph
                        store_counts = Entertainment.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]
                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)

                        # Create a dictionary to store the counts for the current state
                        state_counts_dict = {}
                        
                        # Populate the dictionary with brand counts
                        for entry in brand_counts:
                            state_counts_dict[entry['brand_name']] = entry['store_count']
                        
                        # Fill in 0 for brands with no stores
                        for brand in selected_brand:
                            if brand not in state_counts_dict:
                                state_counts_dict[brand] = 0
                        
                        # Add the state counts dictionary to the result_dict
                        result_dict[state] = state_counts_dict
                    
                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')

                    selected_brand.sort()
                    for state in result_dict:
                        # Sort the state_counts_dict based on selected_brand order
                        sorted_state_counts = {brand: result_dict[state].get(brand, 0) for brand in selected_brand}
                        
                        # Update the result_dict with the sorted state_counts_dict
                        result_dict[state] = sorted_state_counts
                    context = {
                    'industry': industry,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand,
                    'top_cities': top_cities,
                    'state_grouped_cities': state_grouped_cities,
                    'graph': graph,
                    'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                
                else:

                    all_states = set(Entertainment.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Entertainment.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        state_data.append(state_row)

                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits

                    brand_counts = {}

                    # Get a set of all unique brand names
                    all_brands = set(Entertainment.objects.values_list('brand_name', flat=True))
                    all_brands = sorted(list(all_brands))
                    data = []

                    for state in selected_state:
                        brand_counts[state] = {}
                        store_counts = Entertainment.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]
                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)

                        # Query to get the count of stores for each brand in the given state
                        stores_count = (
                            Entertainment.objects
                            .filter(state=state)
                            .values('brand_name')
                            .annotate(store_count=Count('store_name'))
                        )

                        # Populate the brand_counts dictionary
                        for brand in all_brands:
                            # If the brand is present in the stores_count result, use its count; otherwise, set it to 0
                            brand_count = next((entry['store_count'] for entry in stores_count if entry['brand_name'] == brand), 0)
                            brand_counts[state][brand] = brand_count

                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')

                    context = {
                        'industry': industry,
                        'brand_counts': brand_counts,
                        'all_brands': all_brands,
                        'selected_state': selected_state,
                        'selected_brand': selected_brand,
                        'top_cities': top_cities,
                        'graph': graph,
                        'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                    
            elif selected_brand:
                result_dict = {}

                # Get distinct states from the database
                distinct_states = Entertainment.objects.values('state').distinct()
                distinct_states = sorted(distinct_states, key=lambda x: x['state'])
                data = []
                state_data = []
                # Iterate through each state
                for state_info in distinct_states:
                    state_name = state_info['state']
                    state_row = {'state': state_name}
                    # Filter the data for the current state
                    state_whole_data = Entertainment.objects.filter(state=state_name)

                    #graph
                    store_counts = Entertainment.objects.filter(state=state_name, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                    if len(store_counts) == 0:
                        store_counts = [{'state': state_name, 'store_count': 0}]
                        state_row['store_counts'] = 0
                    else:
                        state_row['store_counts'] = store_counts[0]['store_count']
                    state_data.append(state_row)
                    state_graph_data = {
                        'x': [state_name],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state_name
                    }
                    data.append(state_graph_data)

                    # Create a sub-dictionary for the current state
                    state_dict = {}

                    # Iterate through selected brands
                    for brand_name in selected_brand:
                        # Count the number of stores for the current brand in the current state
                        store_count = state_whole_data.filter(brand_name=brand_name).count()

                        # Add the brand count to the sub-dictionary
                        state_dict[brand_name] = store_count

                    # Add the sub-dictionary to the result dictionary
                    result_dict[state_name] = state_dict

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'}
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')

                context = {
                    'industry': industry,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'graph': graph,
                    'state_data': state_data
                }
                return render(request, 'filter.html',context)
            
            else:
                result = (
                    Entertainment.objects
                    .values('state', 'brand_name')
                    .annotate(count=Coalesce(Count('store_name'), 0))
                )

                # Create a dictionary to store the result with default values set to 0
                state_brand_counts = {}

                # Populate the dictionary with the query result
                for entry in result:
                    state = entry['state']
                    brand_name = entry['brand_name']
                    count = entry['count']

                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    state_brand_counts[state][brand_name] = count

                # Add entries with count 0 for any missing combinations
                all_states = set(Entertainment.objects.values_list('state', flat=True).distinct())
                all_brands = set(Entertainment.objects.values_list('brand_name', flat=True).distinct())
                # print(sorted(all_states))
                # print(sorted(all_brands))
                all_brands = sorted(list(all_brands))
                for state in all_states:
                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    for brand_name in all_brands:
                        if brand_name not in state_brand_counts[state]:
                            state_brand_counts[state][brand_name] = 0


                state_data = []
                data = []
                for state in all_states:
                    state_row = {'state': state}
                    
                    # Fetch state census data
                    state_census_data = State_census.objects.filter(state_name=state).first()
                    population = None
                    if state_census_data:
                        state_row['total_population'] = round(state_census_data.total_population /  100000 , 2) 
                        population = state_census_data.total_population
                    else:
                        state_row['total_population'] = 0
                    
                    # Fetch store counts
                    queryset = Entertainment.objects.filter(state=state)
                    store_counts = queryset.values('state').annotate(store_count=Count('store_name'))


                    state_graph_data = {
                        'x': [state],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state
                    }
                    data.append(state_graph_data)
                    
                    if store_counts:
                        state_row['store_counts'] = store_counts[0]['store_count']
                        # Calculate ratio
                        if population is not None:
                            state_row['ratio'] = round ( (state_row['store_counts'] / population ) * 10000, 2 )
                        else:
                            state_row['ratio'] = 0
                    else:
                        state_row['store_counts'] = 0
                        state_row['ratio'] = 0

                    state_data.append(state_row)

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'}
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')

                rows = []
                for state, brand_counts in state_brand_counts.items():
                    row = {'state': state}
                    for brand in all_brands:
                        row[brand] = brand_counts.get(brand, 0)
                    rows.append(row)
                headers = rows[0].keys()
                table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)
                
                rows = sorted(rows, key=lambda x: x['state'])
                state_data = sorted(state_data, key=lambda x: x['state'])

                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    # 'table': html_table,
                    'state_data': state_data,
                    'graph': graph,
                    'headers':headers, 
                    'table_data':table_data,
                    'industry': industry,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand
                }
                
                return render(request, 'filter.html', context)
            
        elif selected_industry == 'Supermarket':
            industry = 'Supermarket'
            if selected_state:
                if selected_brand:

                    all_states = set(Supermarket.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Supermarket.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        
                        state_data.append(state_row)

                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits

                    queryset = Supermarket.objects.filter(state__in=selected_state, brand_name__in=selected_brand)
                    
                    # Use annotate and values to group by city and count the number of stores
                    city_counts = queryset.values('state', 'city').annotate(store_count=Count('store_name'))

                    # Order the results in descending order of store_count
                    sorted_city_counts = city_counts.order_by('-state', '-store_count')

                    # Display only the top 5 cities for each state
                    state_grouped_cities = {}
                    for city_data in sorted_city_counts:
                        state = city_data['state']
                        city = city_data['city']
                        store_count = city_data['store_count']

                        if state not in state_grouped_cities:
                            state_grouped_cities[state] = {'count': 0, 'cities': []}

                        if state_grouped_cities[state]['count'] < 5:
                            state_grouped_cities[state]['cities'].append({'city': city, 'store_count': store_count})
                            state_grouped_cities[state]['count'] += 1


                    result_dict = {}
                    data = []
                    # Loop through each state in the state_list
                    for state in selected_state:
                        # Filter data based on the current state and brand list
                        filtered_data = Supermarket.objects.filter(state=state, brand_name__in=selected_brand)
                        
                        # Aggregate the count of stores for each brand
                        brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                        

                        #graph
                        store_counts = Supermarket.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]
                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)

                        # Create a dictionary to store the counts for the current state
                        state_counts_dict = {}
                        
                        # Populate the dictionary with brand counts
                        for entry in brand_counts:
                            state_counts_dict[entry['brand_name']] = entry['store_count']
                        
                        # Fill in 0 for brands with no stores
                        for brand in selected_brand:
                            if brand not in state_counts_dict:
                                state_counts_dict[brand] = 0
                        
                        # Add the state counts dictionary to the result_dict
                        result_dict[state] = state_counts_dict
                    
                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')

                    selected_brand.sort()
                    for state in result_dict:
                        # Sort the state_counts_dict based on selected_brand order
                        sorted_state_counts = {brand: result_dict[state].get(brand, 0) for brand in selected_brand}
                        
                        # Update the result_dict with the sorted state_counts_dict
                        result_dict[state] = sorted_state_counts
                    context = {
                        'industry': industry,
                        'result_dict': result_dict,
                        'selected_state': selected_state,
                        'selected_brand': selected_brand,
                        'top_cities': top_cities,
                        'state_grouped_cities': state_grouped_cities,
                        'graph': graph,
                        'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                else:

                    all_states = set(Supermarket.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Supermarket.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        state_data.append(state_row)

                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits

                    brand_counts = {}

                    # Get a set of all unique brand names
                    all_brands = set(Supermarket.objects.values_list('brand_name', flat=True))
                    all_brands = sorted(list(all_brands))
                    data = []

                    for state in selected_state:
                        brand_counts[state] = {}
                        store_counts = Supermarket.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]
                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)

                        # Query to get the count of stores for each brand in the given state
                        stores_count = (
                            Supermarket.objects
                            .filter(state=state)
                            .values('brand_name')
                            .annotate(store_count=Count('store_name'))
                        )

                        # Populate the brand_counts dictionary
                        for brand in all_brands:
                            # If the brand is present in the stores_count result, use its count; otherwise, set it to 0
                            brand_count = next((entry['store_count'] for entry in stores_count if entry['brand_name'] == brand), 0)
                            brand_counts[state][brand] = brand_count

                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')
                    context = {
                        'industry': industry,
                        'brand_counts': brand_counts,
                        'all_brands': all_brands,
                        'selected_state': selected_state,
                        'selected_brand': selected_brand,
                        'top_cities': top_cities,
                        'graph': graph,
                        'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                    
            elif selected_brand:
                result_dict = {}

                # Get distinct states from the database
                distinct_states = Supermarket.objects.values('state').distinct()
                distinct_states = sorted(distinct_states, key=lambda x: x['state'])
                data = []
                state_data = []
                # Iterate through each state
                for state_info in distinct_states:
                    state_name = state_info['state']
                    state_row = {'state': state_name}
                    # Filter the data for the current state
                    state_whole_data = Supermarket.objects.filter(state=state_name)

                    #graph
                    store_counts = Supermarket.objects.filter(state=state_name, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                    if len(store_counts) == 0:
                        store_counts = [{'state': state_name, 'store_count': 0}]
                        state_row['store_counts'] = 0
                    else:
                        state_row['store_counts'] = store_counts[0]['store_count']
                    state_data.append(state_row)
                    state_graph_data = {
                        'x': [state_name],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state_name
                    }
                    data.append(state_graph_data)

                    # Create a sub-dictionary for the current state
                    state_dict = {}

                    # Iterate through selected brands
                    for brand_name in selected_brand:
                        # Count the number of stores for the current brand in the current state
                        store_count = state_whole_data.filter(brand_name=brand_name).count()

                        # Add the brand count to the sub-dictionary
                        state_dict[brand_name] = store_count

                    # Add the sub-dictionary to the result dictionary
                    result_dict[state_name] = state_dict

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'}
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')

                context = {
                    'industry': industry,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'graph': graph,
                    'state_data': state_data
                }
                return render(request, 'filter.html',context)
            
            else:
                result = (
                    Supermarket.objects
                    .values('state', 'brand_name')
                    .annotate(count=Coalesce(Count('store_name'), 0))
                )

                # Create a dictionary to store the result with default values set to 0
                state_brand_counts = {}

                # Populate the dictionary with the query result
                for entry in result:
                    state = entry['state']
                    brand_name = entry['brand_name']
                    count = entry['count']

                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    state_brand_counts[state][brand_name] = count

                # Add entries with count 0 for any missing combinations
                all_states = set(Supermarket.objects.values_list('state', flat=True).distinct())
                all_brands = set(Supermarket.objects.values_list('brand_name', flat=True).distinct())
                # print(sorted(all_states))
                # print(sorted(all_brands))
                all_brands = sorted(list(all_brands))
                for state in all_states:
                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    for brand_name in all_brands:
                        if brand_name not in state_brand_counts[state]:
                            state_brand_counts[state][brand_name] = 0

                rows = []
                
                for state, brand_counts in state_brand_counts.items():
                    row = {'state': state}
                    for brand in all_brands:
                        row[brand] = brand_counts.get(brand, 0)
                    
                    
                    rows.append(row)
                headers = rows[0].keys()

                state_data = []
                data = []
                map_counts = []
                for state in all_states:
                    state_row = {'state': state}
                    
                    # Fetch state census data
                    state_census_data = State_census.objects.filter(state_name=state).first()
                    population = None
                    if state_census_data:
                        state_row['total_population'] = round(state_census_data.total_population /  100000 , 2) 
                        population = state_census_data.total_population
                    else:
                        state_row['total_population'] = 0
                    
                    # Fetch store counts
                    queryset = Supermarket.objects.filter(state=state)
                    store_counts = queryset.values('state').annotate(store_count=Count('store_name'))
                    map_counts.append(store_counts)

                    state_graph_data = {
                        'x': [state],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state
                    }
                    data.append(state_graph_data)
                    
                    if store_counts:
                        state_row['store_counts'] = store_counts[0]['store_count']
                        # Calculate ratio
                        if population is not None:
                            state_row['ratio'] = round ( (state_row['store_counts'] / population ) * 10000, 2 )
                        else:
                            state_row['ratio'] = 0    
                    else:
                        state_row['store_counts'] = 0
                        state_row['ratio'] = 0

                    state_data.append(state_row)

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'}
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')
                # for r in rows:
                #     state = r['state']
                # headers.append('Ratio')
                # table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)
                rows = sorted(rows, key=lambda x: x['state'])
                state_data = sorted(state_data, key=lambda x: x['state'])
                
                
                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    # 'table': html_table,
                   
                    'state_data': state_data,
                    'graph': graph,
                    'headers':headers, 
                    # 'table_data':table_data,
                    'industry': industry,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand,
                    'map_counts': map_counts
                }
                
                return render(request, 'filter.html', context)
            
        elif selected_industry == 'Telecom':
            industry = 'Telecom'
            if selected_state:
                if selected_brand:

                    all_states = set(Telecom.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Telecom.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        
                        state_data.append(state_row)

                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits

                    queryset = Telecom.objects.filter(state__in=selected_state, brand_name__in=selected_brand)
                    
                    # Use annotate and values to group by city and count the number of stores
                    city_counts = queryset.values('state', 'city').annotate(store_count=Count('store_name'))

                    # Order the results in descending order of store_count
                    sorted_city_counts = city_counts.order_by('-state', '-store_count')

                    # Display only the top 5 cities for each state
                    state_grouped_cities = {}
                    for city_data in sorted_city_counts:
                        state = city_data['state']
                        city = city_data['city']
                        store_count = city_data['store_count']

                        if state not in state_grouped_cities:
                            state_grouped_cities[state] = {'count': 0, 'cities': []}

                        if state_grouped_cities[state]['count'] < 5:
                            state_grouped_cities[state]['cities'].append({'city': city, 'store_count': store_count})
                            state_grouped_cities[state]['count'] += 1
   
                    
                    result_dict = {}
                    data = []
                    # Loop through each state in the state_list
                    for state in selected_state:
                        # Filter data based on the current state and brand list
                        filtered_data = Telecom.objects.filter(state=state, brand_name__in=selected_brand)
                        
                        # Aggregate the count of stores for each brand
                        brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                        
                        #graph
                        store_counts = Telecom.objects.filter(state=state, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]
                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)

                        # Create a dictionary to store the counts for the current state
                        state_counts_dict = {}
                        
                        # Populate the dictionary with brand counts
                        for entry in brand_counts:
                            state_counts_dict[entry['brand_name']] = entry['store_count']
                    

                        # Fill in 0 for brands with no stores
                        for brand in selected_brand:
                            if brand not in state_counts_dict:
                                state_counts_dict[brand] = 0

                        # Add the state counts dictionary to the result_dict
                        result_dict[state] = state_counts_dict
                        
                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')
                    
                    selected_brand.sort()
                    for state in result_dict:
                        # Sort the state_counts_dict based on selected_brand order
                        sorted_state_counts = {brand: result_dict[state].get(brand, 0) for brand in selected_brand}
                        
                        # Update the result_dict with the sorted state_counts_dict
                        result_dict[state] = sorted_state_counts
                    context = {
                    'industry': industry,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand,
                    'top_cities': top_cities,
                    'state_grouped_cities': state_grouped_cities,
                    'graph': graph,
                    'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                
                else:
                    all_states = set(Telecom.objects.values_list('state', flat=True).distinct())
                    state_data = []
                    for state in all_states:
                        if state in selected_state:
                            state_row = {'state': state}
                            store_counts = Telecom.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                            if store_counts:
                                state_row['store_counts'] = store_counts[0]['store_count']
                            else:
                                state_row['store_counts'] = 0
                        else:
                            state_row = {'state':state} 
                            state_row['store_counts'] = 0
                        state_data.append(state_row)

                    top_cities = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=selected_state)
                    
                    for city in top_cities:
                        city.total_population = round(city.total_population / 100000, 2)  # Divide total_population by 1 lakh and round to 2 digits
                        city.total_males = round(city.total_males / 100000, 2)  # Divide total_males by 1 lakh and round to 2 digits
                        city.total_female = round(city.total_female / 100000, 2)  # Divide total_female by 1 lakh and round to 2 digits

                    brand_counts = {}

                    # Get a set of all unique brand names
                    all_brands = set(Telecom.objects.values_list('brand_name', flat=True))
                    all_brands = sorted(list(all_brands))
                    data = []
                    for state in selected_state:
                        brand_counts[state] = {}
                        store_counts = Telecom.objects.filter(state=state).values('state').annotate(store_count=Count('id'))
                        if len(store_counts) == 0:
                            store_counts = [{'state': state, 'store_count': 0}]
                        state_graph_data = {
                            'x': [state],
                            'y': [store_counts[0]['store_count']],
                            'type': 'bar',
                            'name': state
                        }
                        data.append(state_graph_data)

                        # Query to get the count of stores for each brand in the given state
                        stores_count = (
                            Telecom.objects
                            .filter(state=state)
                            .values('brand_name')
                            .annotate(store_count=Count('store_name'))
                        )

                        # Populate the brand_counts dictionary
                        for brand in all_brands:
                            # If the brand is present in the stores_count result, use its count; otherwise, set it to 0
                            brand_count = next((entry['store_count'] for entry in stores_count if entry['brand_name'] == brand), 0)
                            brand_counts[state][brand] = brand_count
                    # print(brand_counts)
                    layout = {
                        'title': 'Store Count by State',
                        'xaxis': {'title': 'State'},
                        'yaxis': {'title': 'Store Count'}
                    }
                    data = sorted(data, key=lambda x: x['x'][0])
                    graph = plot({'data': data, 'layout': layout}, output_type='div')

                    context = {
                        'industry': industry,
                        'brand_counts': brand_counts,
                        'all_brands': all_brands,
                        'selected_state': selected_state,
                        'selected_brand': selected_brand,
                        'top_cities': top_cities,
                        'graph': graph,
                        'state_data': state_data
                    }
                    return render(request, 'filter.html',context)
                    
            elif selected_brand:
                result_dict = {}

                # Get distinct states from the database
                distinct_states = Telecom.objects.values('state').distinct()
                distinct_states = sorted(distinct_states, key=lambda x: x['state'])
                data = []
                state_data = []
                # Iterate through each state
                for state_info in distinct_states:
                    state_name = state_info['state']
                    state_row = {'state': state_name}
                    # Filter the data for the current state
                    state_whole_data = Telecom.objects.filter(state=state_name)

                    #graph
                    store_counts = Telecom.objects.filter(state=state_name, brand_name__in=selected_brand).values('state').annotate(store_count=Count('id'))
                    if len(store_counts) == 0:
                        store_counts = [{'state': state_name, 'store_count': 0}]
                        state_row['store_counts'] = 0
                    else:
                        state_row['store_counts'] = store_counts[0]['store_count']
                    state_data.append(state_row)
                    state_graph_data = {
                        'x': [state_name],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state_name
                    }
                    data.append(state_graph_data)

                    # Create a sub-dictionary for the current state
                    state_dict = {}

                    # Iterate through selected brands
                    for brand_name in selected_brand:
                        # Count the number of stores for the current brand in the current state
                        store_count = state_whole_data.filter(brand_name=brand_name).count()

                        # Add the brand count to the sub-dictionary
                        state_dict[brand_name] = store_count

                    # Add the sub-dictionary to the result dictionary
                    result_dict[state_name] = state_dict

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'}
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')

                context = {
                    'industry': industry,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'selected_state': selected_state,
                    'graph': graph,
                    'state_data': state_data
                }
                return render(request, 'filter.html',context)
            
            else:
                result = (
                    Telecom.objects
                    .values('state', 'brand_name')
                    .annotate(count=Coalesce(Count('store_name'), 0))
                )

                # Create a dictionary to store the result with default values set to 0
                state_brand_counts = {}

                # Populate the dictionary with the query result
                for entry in result:
                    state = entry['state']
                    brand_name = entry['brand_name']
                    count = entry['count']

                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    state_brand_counts[state][brand_name] = count

                # Add entries with count 0 for any missing combinations
                all_states = set(Telecom.objects.values_list('state', flat=True).distinct())
                all_brands = set(Telecom.objects.values_list('brand_name', flat=True).distinct())
                # print(sorted(all_states))
                # print(sorted(all_brands))
                all_brands = sorted(list(all_brands))
                for state in all_states:
                    if state not in state_brand_counts:
                        state_brand_counts[state] = {}

                    for brand_name in all_brands:
                        if brand_name not in state_brand_counts[state]:
                            state_brand_counts[state][brand_name] = 0


                state_data = []
                data = []
                for state in all_states:
                    state_row = {'state': state}
                    
                    # Fetch state census data
                    state_census_data = State_census.objects.filter(state_name=state).first()
                    population = None
                    if state_census_data:
                        state_row['total_population'] = round(state_census_data.total_population /  100000 , 2) 
                        population = state_census_data.total_population
                    else:
                        state_row['total_population'] = 0
                    
                    # Fetch store counts
                    queryset = Telecom.objects.filter(state=state)
                    store_counts = queryset.values('state').annotate(store_count=Count('store_name'))
                    

                    state_graph_data = {
                        'x': [state],
                        'y': [store_counts[0]['store_count']],
                        'type': 'bar',
                        'name': state
                    }
                    data.append(state_graph_data)
                    
                    if store_counts:
                        state_row['store_counts'] = store_counts[0]['store_count']
                        # Calculate ratio
                        if population is not None:
                            state_row['ratio'] = round ( (state_row['store_counts'] / population ) * 10000, 2 )
                        else:
                            state_row['ratio'] = 0
                    else:
                        state_row['store_counts'] = 0
                        state_row['ratio'] = 0

                    state_data.append(state_row)

                layout = {
                    'title': 'Store Count by State',
                    'xaxis': {'title': 'State'},
                    'yaxis': {'title': 'Store Count'}
                }
                data = sorted(data, key=lambda x: x['x'][0])
                graph = plot({'data': data, 'layout': layout}, output_type='div')

                rows = []
                for state, brand_counts in state_brand_counts.items():
                    row = {'state': state}
                    for brand in all_brands:
                        row[brand] = brand_counts.get(brand, 0)
                    rows.append(row)
                headers = rows[0].keys()
                table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)

                rows = sorted(rows, key=lambda x: x['state'])
                state_data = sorted(state_data, key=lambda x: x['state'])
                
                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    'state_data': state_data,
                    'graph': graph,
                    # 'table': html_table,
                    'headers':headers, 
                    'table_data':table_data,
                    'industry': industry,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand
                }
                
                return render(request, 'filter.html', context)
    else:
        # Handle other HTTP methods if needed
        if industry and state and brand:
            industry = request.GET.get('industry', '')
            state = request.GET.get('state', '')
            brand = request.GET.get('brand', '')

            selected_industry = request.GET.get('industries')
            selected_state = request.GET.getlist('states')
            selected_brand = request.GET.getlist('brands')

            if industry == 'Apparel':
                filtered_data = Apparel.objects.filter(state=state, brand_name=brand)
                filtered_data_count = filtered_data.count()
                paginator = Paginator(filtered_data, 20)  # Show 20 items per page

                page = request.GET.get('page')
                try:
                    filtered_data = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    filtered_data = paginator.page(1)
                except EmptyPage:
                    # If page is out of range, deliver last page of results.
                    filtered_data = paginator.page(paginator.num_pages)
                context = {'filtered_data':filtered_data, 'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count, 'selected_state': selected_state, 'selected_brand': selected_brand}

                return render(request, 'filter.html', context)

            elif industry == 'Automobile':
                filtered_data = Automobile.objects.filter(state=state, brand_name=brand)
                filtered_data_count = filtered_data.count()
                paginator = Paginator(filtered_data, 20)  # Show 20 items per page

                page = request.GET.get('page')
                try:
                    filtered_data = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    filtered_data = paginator.page(1)
                except EmptyPage:
                    # If page is out of range, deliver last page of results.
                    filtered_data = paginator.page(paginator.num_pages)
                context = {'filtered_data':filtered_data, 'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count, 'selected_state': selected_state, 'selected_brand': selected_brand}

                return render(request, 'filter.html', context)
            
            elif industry == 'Electronic':
                filtered_data = Electronic.objects.filter(state=state, brand_name=brand)
                filtered_data_count = filtered_data.count()
                paginator = Paginator(filtered_data, 20) 
                page = request.GET.get('page')
                try:
                    filtered_data = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    filtered_data = paginator.page(1)
                except EmptyPage:
                    # If page is out of range, deliver last page of results.
                    filtered_data = paginator.page(paginator.num_pages)
                context = {'filtered_data':filtered_data,'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count}

                return render(request, 'filter.html', context)
            
            elif industry == 'Entertainment':
                filtered_data = Entertainment.objects.filter(state=state, brand_name=brand)
                filtered_data_count = filtered_data.count()
                paginator = Paginator(filtered_data, 20) 
                page = request.GET.get('page')
                try:
                    filtered_data = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    filtered_data = paginator.page(1)
                except EmptyPage:
                    # If page is out of range, deliver last page of results.
                    filtered_data = paginator.page(paginator.num_pages)
                context = {'filtered_data':filtered_data,'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count}

                return render(request, 'filter.html', context)
            
            elif industry == 'Supermarket':
                filtered_data = Supermarket.objects.filter(state=state, brand_name=brand)
                filtered_data_count = filtered_data.count()
                paginator = Paginator(filtered_data, 20) 
                page = request.GET.get('page')
                try:
                    filtered_data = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    filtered_data = paginator.page(1)
                except EmptyPage:
                    # If page is out of range, deliver last page of results.
                    filtered_data = paginator.page(paginator.num_pages)
                context = {'filtered_data':filtered_data,'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count}

                return render(request, 'filter.html', context)
            
            elif industry == 'Telecom':
                filtered_data = Telecom.objects.filter(state=state, brand_name=brand)
                filtered_data_count = filtered_data.count()
                paginator = Paginator(filtered_data, 20) 
                page = request.GET.get('page')
                try:
                    filtered_data = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    filtered_data = paginator.page(1)
                except EmptyPage:
                    # If page is out of range, deliver last page of results.
                    filtered_data = paginator.page(paginator.num_pages)
                context = {'filtered_data':filtered_data,'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count}
                
                return render(request, 'filter.html', context)
        else:
            return render(request, 'index.html')
    
def store_info(request):
    industry = request.GET.get('industry', '')
    state = request.GET.get('state', '')
    brand = request.GET.get('brand', '')
  
    
    selected_state = request.GET.get('selected_states', '').split(',')
    selected_brand = request.GET.get('selected_brands', '').split(',')
    
    if industry and state and brand:
    
        if industry == 'Apparel':
            filtered_data = Apparel.objects.filter(state=state, brand_name=brand)
            filtered_data_count = filtered_data.count()
            paginator = Paginator(filtered_data, 20)  # Show 10 items per page

            page = request.GET.get('page')
            try:
                filtered_data = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                filtered_data = paginator.page(1)
            except EmptyPage:
                # If page is out of range, deliver last page of results.
                filtered_data = paginator.page(paginator.num_pages)
            context = {'filtered_data':filtered_data, 'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count, 'selected_state': selected_state, 'selected_brand': selected_brand}

            return render(request, 'filter.html', context)

        elif industry == 'Automobile':
            filtered_data = Automobile.objects.filter(state=state, brand_name=brand)
            filtered_data_count = filtered_data.count()
            paginator = Paginator(filtered_data, 20)  # Show 10 items per page

            page = request.GET.get('page')
            try:
                filtered_data = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                filtered_data = paginator.page(1)
            except EmptyPage:
                # If page is out of range, deliver last page of results.
                filtered_data = paginator.page(paginator.num_pages)
            context = {'filtered_data':filtered_data, 'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count, 'selected_state': selected_state, 'selected_brand': selected_brand}

            return render(request, 'filter.html', context)
        
        elif industry == 'Electronic':
            filtered_data = Electronic.objects.filter(state=state, brand_name=brand)
            filtered_data_count = filtered_data.count()
            paginator = Paginator(filtered_data, 20) 
            page = request.GET.get('page')
            try:
                filtered_data = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                filtered_data = paginator.page(1)
            except EmptyPage:
                # If page is out of range, deliver last page of results.
                filtered_data = paginator.page(paginator.num_pages)
            context = {'filtered_data':filtered_data,'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count, 'selected_state': selected_state, 'selected_brand': selected_brand}

            return render(request, 'filter.html', context)
        
        elif industry == 'Entertainment':
            filtered_data = Entertainment.objects.filter(state=state, brand_name=brand)
            filtered_data_count = filtered_data.count()
            paginator = Paginator(filtered_data, 20) 
            page = request.GET.get('page')
            try:
                filtered_data = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                filtered_data = paginator.page(1)
            except EmptyPage:
                # If page is out of range, deliver last page of results.
                filtered_data = paginator.page(paginator.num_pages)
            context = {'filtered_data':filtered_data,'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count, 'selected_state': selected_state, 'selected_brand': selected_brand}

            return render(request, 'filter.html', context)
        
        elif industry == 'Supermarket':
            filtered_data = Supermarket.objects.filter(state=state, brand_name=brand)
            filtered_data_count = filtered_data.count()
            paginator = Paginator(filtered_data, 20) 
            page = request.GET.get('page')
            try:
                filtered_data = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                filtered_data = paginator.page(1)
            except EmptyPage:
                # If page is out of range, deliver last page of results.
                filtered_data = paginator.page(paginator.num_pages)
            context = {'filtered_data':filtered_data,'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count, 'selected_state': selected_state, 'selected_brand': selected_brand}

            return render(request, 'filter.html', context)
        
        elif industry == 'Telecom':
            filtered_data = Telecom.objects.filter(state=state, brand_name=brand)
            filtered_data_count = filtered_data.count()
            paginator = Paginator(filtered_data, 20) 
            page = request.GET.get('page')
            try:
                filtered_data = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                filtered_data = paginator.page(1)
            except EmptyPage:
                # If page is out of range, deliver last page of results.
                filtered_data = paginator.page(paginator.num_pages)
            context = {'filtered_data':filtered_data,'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count, 'selected_state': selected_state, 'selected_brand': selected_brand}
            
            return render(request, 'filter.html', context)
    # You can fetch detailed information based on the state and brand
    # For now, let's just pass state and brand to the template

    else:
        return render(request, 'filter.html')

def get_data(request, industry):

    data = {}

    if industry == 'Industry':
        states = []
        brands = []

        data['states'] = states
        data['brands'] = brands

    elif industry == 'Apparel':
        states = list(Apparel.objects.values_list('state', flat=True).distinct())
        brands = list(Apparel.objects.values_list('brand_name', flat=True).distinct())

        data['states'] = states
        data['brands'] = brands

    elif industry == 'Automobile':
        states = list(Automobile.objects.values_list('state', flat=True).distinct())
        brands = list(Automobile.objects.values_list('brand_name', flat=True).distinct())
        
        data['states'] = states
        data['brands'] = brands

    elif industry == 'Electronic':
        states = list(Electronic.objects.values_list('state', flat=True).distinct())
        brands = list(Electronic.objects.values_list('brand_name', flat=True).distinct())
        
        data['states'] = states
        data['brands'] = brands
    elif industry == 'Entertainment':
        states = list(Entertainment.objects.values_list('state', flat=True).distinct())
        brands = list(Entertainment.objects.values_list('brand_name', flat=True).distinct())
        
        data['states'] = states
        data['brands'] = brands
    elif industry == 'Supermarket':
        states = list(Supermarket.objects.values_list('state', flat=True).distinct())
        brands = list(Supermarket.objects.values_list('brand_name', flat=True).distinct())
        
        data['states'] = states
        data['brands'] = brands
    elif industry == 'Telecom':
        states = list(Telecom.objects.values_list('state', flat=True).distinct())
        brands = list(Telecom.objects.values_list('brand_name', flat=True).distinct())
        
        data['states'] = states
        data['brands'] = brands
    return JsonResponse(data)


def top(request):
    name = ['Gujarat', 'Maharashtra']
    data = Top_five_populated_cities_of_each_state.objects.filter(state_name__in=name)

    return render(request, 'top.html', {'data': data})

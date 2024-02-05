from django.db.models import Count
from django.shortcuts import render
import pandas as pd
from .models import *
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import Coalesce
# Create your views here.
def index(request):
    return render(request, 'index.html')

def search_results(request):
    if request.method == 'POST':

        selected_industry = request.POST.get('industries')
        selected_state = request.POST.get('states')
        selected_brand = request.POST.get('brands')
        print(selected_industry, selected_state, selected_brand)
        if selected_industry == 'automobile':
            industry = 'Automobile'
            if selected_state:
                if selected_brand:
                    filtered_data = Automobile.objects.filter(state__iexact=selected_state, brand_name__iexact=selected_brand)
                    brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                    context = {
                    'industry': industry,
                    'filtered_data': filtered_data,
                    'brand_counts': brand_counts,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand
                    }
                    return render(request, 'filter.html',context)
                
                else:
                    filtered_data = Automobile.objects.filter(state__iexact=selected_state)
                    brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                    context = {
                        'industry': industry,
                        'filtered_data': filtered_data,
                        'brand_counts': brand_counts,
                        'selected_state': selected_state
                    }
                    return render(request, 'filter.html',context)
                    
            elif selected_brand:
                filtered_data = Automobile.objects.filter(brand_name__iexact=selected_brand)
                stores_count_by_state = filtered_data.values('state').annotate(num_stores=Count('state'))
                result_dict = {item['state']: item['num_stores'] for item in stores_count_by_state}
                context = {
                    'industry': industry,
                    'filtered_data': filtered_data,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'stores_count_by_state': stores_count_by_state
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
                table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)
                
                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    # 'table': html_table,
                    'headers':headers, 
                    'table_data':table_data,
                    'industry': industry
                }
                
                return render(request, 'filter.html', context)
        
        elif selected_industry == 'electronics':
            industry = 'Electronic'
            if selected_state:
                if selected_brand:
                    filtered_data = Electronic.objects.filter(state__iexact=selected_state, brand_name__iexact=selected_brand)
                    brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                    context = {
                    'industry': industry,
                    'filtered_data': filtered_data,
                    'brand_counts': brand_counts,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand
                    }
                    return render(request, 'filter.html',context)
                
                else:
                    filtered_data = Electronic.objects.filter(state__iexact=selected_state)
                    brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                    context = {
                        'industry': industry,
                        'filtered_data': filtered_data,
                        'brand_counts': brand_counts,
                        'selected_state': selected_state
                    }
                    return render(request, 'filter.html',context)
                    
            elif selected_brand:
                filtered_data = Electronic.objects.filter(brand_name__iexact=selected_brand)
                stores_count_by_state = filtered_data.values('state').annotate(num_stores=Count('state'))
                result_dict = {item['state']: item['num_stores'] for item in stores_count_by_state}
                context = {
                    'industry': industry,
                    'filtered_data': filtered_data,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'stores_count_by_state': stores_count_by_state
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
                table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)
                
                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    # 'table': html_table,
                    'headers':headers, 
                    'table_data':table_data,
                    'industry': industry
                }
                
                return render(request, 'filter.html', context)
           
        elif selected_industry == 'entertainment':
            industry = 'Entertainment'
            if selected_state:
                if selected_brand:
                    filtered_data = Entertainment.objects.filter(state__iexact=selected_state, brand_name__iexact=selected_brand)
                    brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                    context = {
                    'industry': industry,
                    'filtered_data': filtered_data,
                    'brand_counts': brand_counts,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand
                    }
                    return render(request, 'filter.html',context)
                else:
                    filtered_data = Entertainment.objects.filter(state__iexact=selected_state)
                    brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                    context = {
                        'industry': industry,
                        'filtered_data': filtered_data,
                        'brand_counts': brand_counts,
                        'selected_state': selected_state
                    }
                    return render(request, 'filter.html',context)
                    
            elif selected_brand:
                filtered_data = Entertainment.objects.filter(brand_name__iexact=selected_brand)
                stores_count_by_state = filtered_data.values('state').annotate(num_stores=Count('state'))
                result_dict = {item['state']: item['num_stores'] for item in stores_count_by_state}
                context = {
                    'industry': industry,
                    'filtered_data': filtered_data,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'stores_count_by_state': stores_count_by_state
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
                table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)
                
                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    # 'table': html_table,
                    'headers':headers, 
                    'table_data':table_data,
                    'industry': industry
                }
                
                return render(request, 'filter.html', context)
            
        elif selected_industry == 'supermarket':
            industry = 'Supermarket'
            if selected_state:
                if selected_brand:
                    filtered_data = Supermarket.objects.filter(state__iexact=selected_state, brand_name__iexact=selected_brand)
                    brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                    context = {
                    'industry': industry,
                    'filtered_data': filtered_data,
                    'brand_counts': brand_counts,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand
                    }
                    return render(request, 'filter.html',context)
                else:
                    filtered_data = Supermarket.objects.filter(state__iexact=selected_state)
                    brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                    context = {
                        'industry': industry,
                        'filtered_data': filtered_data,
                        'brand_counts': brand_counts,
                        'selected_state': selected_state
                    }
                    return render(request, 'filter.html',context)
                    
            elif selected_brand:
                filtered_data = Supermarket.objects.filter(brand_name__iexact=selected_brand)
                stores_count_by_state = filtered_data.values('state').annotate(num_stores=Count('state'))
                result_dict = {item['state']: item['num_stores'] for item in stores_count_by_state}
                context = {
                    'industry': industry,
                    'filtered_data': filtered_data,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'stores_count_by_state': stores_count_by_state
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
                table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)
                
                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    # 'table': html_table,
                    'headers':headers, 
                    'table_data':table_data,
                    'industry': industry
                }
                
                return render(request, 'filter.html', context)
            
        elif selected_industry == 'telecom':
            industry = 'Telecom'
            if selected_state:
                if selected_brand:
                    filtered_data = Telecom.objects.filter(state__iexact=selected_state, brand_name__iexact=selected_brand)
                    brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                    context = {
                    'industry': industry,
                    'filtered_data': filtered_data,
                    'brand_counts': brand_counts,
                    'selected_state': selected_state,
                    'selected_brand': selected_brand
                    }
                    return render(request, 'filter.html',context)
                else:
                    filtered_data = Telecom.objects.filter(state__iexact=selected_state)
                    brand_counts = filtered_data.values('brand_name').annotate(store_count=Count('id'))
                    context = {
                        'industry': industry,
                        'filtered_data': filtered_data,
                        'brand_counts': brand_counts,
                        'selected_state': selected_state
                    }
                    return render(request, 'filter.html',context)
                    
            elif selected_brand:
                filtered_data = Telecom.objects.filter(brand_name__iexact=selected_brand)
                stores_count_by_state = filtered_data.values('state').annotate(num_stores=Count('state'))
                result_dict = {item['state']: item['num_stores'] for item in stores_count_by_state}
                context = {
                    'industry': industry,
                    'filtered_data': filtered_data,
                    'selected_brand' : selected_brand,
                    'result_dict': result_dict,
                    'stores_count_by_state': stores_count_by_state
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
                table_data = [[entry[key] for key in headers] for entry in rows]
                # df = pd.DataFrame(rows)
                # html_table = df.to_html(index=False, escape=False)
                
                context ={
                    'state_brand_counts': state_brand_counts,
                    'all_brands': all_brands,
                    'rows': rows,
                    # 'table': html_table,
                    'headers':headers, 
                    'table_data':table_data,
                    'industry': industry
                }
                
                return render(request, 'filter.html', context)
    else:
        # Handle other HTTP methods if needed
        return render(request, 'index.html')
    
def store_info(request):
    industry = request.GET.get('industry', '')
    state = request.GET.get('state', '')
    brand = request.GET.get('brand', '')
    #print('industry:', industry, 'state:', state, 'brand:', brand)
    if industry and state and brand:
    
        if industry == 'Automobile':
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
            context = {'filtered_data':filtered_data, 'industry':industry, 'state':state, 'brand':brand, 'filtered_data_count': filtered_data_count}

            return render(request, 'store_info.html', context)
        
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

            return render(request, 'store_info.html', context)
        
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

            return render(request, 'store_info.html', context)
        
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

            return render(request, 'store_info.html', context)
        
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
            
            return render(request, 'store_info.html', context)
    # You can fetch detailed information based on the state and brand
    # For now, let's just pass state and brand to the template

    else:
        return render(request, 'filter.html')

def get_data(request, industry):
    data = {}

    if industry == 'automobile':
        states = list(Automobile.objects.values_list('state', flat=True).distinct())
        brands = list(Automobile.objects.values_list('brand_name', flat=True).distinct())
        
        data['states'] = states
        data['brands'] = brands
    elif industry == 'electronics':
        states = list(Electronic.objects.values_list('state', flat=True).distinct())
        brands = list(Electronic.objects.values_list('brand_name', flat=True).distinct())
        
        data['states'] = states
        data['brands'] = brands
    elif industry == 'entertainment':
        states = list(Entertainment.objects.values_list('state', flat=True).distinct())
        brands = list(Entertainment.objects.values_list('brand_name', flat=True).distinct())
        
        data['states'] = states
        data['brands'] = brands
    elif industry == 'supermarket':
        states = list(Supermarket.objects.values_list('state', flat=True).distinct())
        brands = list(Supermarket.objects.values_list('brand_name', flat=True).distinct())
        
        data['states'] = states
        data['brands'] = brands
    elif industry == 'telecom':
        states = list(Telecom.objects.values_list('state', flat=True).distinct())
        brands = list(Telecom.objects.values_list('brand_name', flat=True).distinct())
        
        data['states'] = states
        data['brands'] = brands
    return JsonResponse(data)
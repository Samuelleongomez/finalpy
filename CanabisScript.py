
"""
Name:       Samuel Leon Gomez
CS230:      Section 05
Data:       Cannabis Registry
URL:        Link to your web application on Streamlit Cloud (if posted)

Description:
Using pandas for data analysis and manipulation, matplotlib for the creation of graphs and streamlit for displaying the
information and creating interaction with the User. My program shows some interesting insights of Boston Canabis Registry,
the main insights relied on location, in order to see the distribution of cannabis facilities in Boston. Also in the
program we can see what facilities are supported by the state, also under which type of legal entities this facilities
operate, and also the different licenses provided by the state. This program could help us to get a better insight of the
industry in Boston. Also the second tab, includes some features that allow the user to find retail facilities in any
zip code they want. This tab purpose is for the user to play and get more interaction with the program.
"""


import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk
import pandas as pd


# df creation and cleaning
df_cannabis_csv = pd.read_csv("C:\\Users\\17813\\OneDrive\\Escritorio\\Program_3\\Final project\\Cannabis_Registry.csv", index_col="ObjectId")
df_cannabis_csv.drop(["X", "Y", "geom_4326"], axis=1, inplace=True)
df_cannabis_csv.dropna(axis=0, inplace=True)
df_cannabis_csv.rename(columns={"latitude": "lat", "longitude": "lon"}, inplace=True)
#print(df_cannabis_csv['app_license_category'])

tab1, tab2 = st.tabs(["Stats", "Interact"])

with tab1:
    def filter_data(df, business_types=None, zip_codes=None):
        if business_types:
            df = df[df['app_license_category'].isin(business_types)]
        if zip_codes:
            df = df[df['facility_zip_code'].isin(zip_codes)]
        return df

    st.header("Cannabis Stats")

    business_types = df_cannabis_csv['app_license_category'].unique()
    selected_business_types = st.multiselect('Select Business Types', business_types)

    zip_codes = df_cannabis_csv['facility_zip_code'].unique()
    selected_zip_codes = st.multiselect('Select Zip Codes', zip_codes)

    filtered_df = filter_data(df_cannabis_csv, selected_business_types, selected_zip_codes)

    if st.checkbox('Show Dataframe'):
        sort_column = st.selectbox("Select column to sort by", filtered_df.columns)
        sort_order = st.radio("Select sort order", ["Ascending", "Descending"])
        sorted_df = filtered_df.sort_values(by=sort_column, ascending=(sort_order == "Ascending"))
        st.dataframe(sorted_df)

    st.title('Cannabis Registry Data Analysis App')
    st.sidebar.header("Control Panel")

    # Container with Project objectives
    container = st.container()
    container.header("Initial questions")
    container.write("1) What Zip codes in Massashussets have the most active and inactive Cannabis facilities?")
    container.write("2) What is the ratio of facilities supported and not supported by the equity program designation?")
    container.write("3) Under what type legal entity are Cannabis facilities stablished?")
    container.write("4) How are the facility licenses for different purposes distributed? and what could be deduced from this disribution?")
    st.header("Complete Cannabis Registry Data")

    # Question 1
    st.subheader('1) Zip Codes with most active and inactive cannabis facilities')
    status = ['', 'Active', 'Inactive']
    df_status = df_cannabis_csv["app_license_status"].value_counts()
    selected_status = st.sidebar.radio(" 1.Facility Status", status)

    if selected_status == 'Active':
        filtered_data = df_cannabis_csv[df_cannabis_csv['app_license_status'] == 'Active']
        bar_color = 'Green'

    elif selected_status == 'Inactive':
        filtered_data = df_cannabis_csv[df_cannabis_csv['app_license_status'] == 'Inactive']
        bar_color = 'Red'

    else:
        filtered_data = df_cannabis_csv
        bar_color = 'Blue'

    status_count = filtered_data['app_license_status'].value_counts()
    st.write(status_count)

    fig, ax = plt.subplots()
    status_count.plot(kind='bar', color=bar_color, ax=ax)

    ax.set_title("Distribution of Cannabis Facilities by Status", fontsize=16)
    ax.set_xlabel("Status", fontsize=14)
    ax.set_ylabel("Number of Facilities", fontsize=14)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    st.pyplot(fig)

    # Question 2

    st.subheader(' 2)Facilities Supported vs. Not Supported by the State')

    filter_category = st.sidebar.selectbox(" 2.Filter by category", ['None', 'Business Type', 'Zip Code'])

    if filter_category != 'None':
        if filter_category == 'Business Type':
            business_types = df_cannabis_csv['app_license_category'].unique()
            selected_type = st.selectbox("Select Business Type", business_types)
            filtered_df = df_cannabis_csv[df_cannabis_csv['app_license_category'] == selected_type]
        else:
            zip_codes = df_cannabis_csv['facility_zip_code'].unique()
            selected_zip = st.selectbox("Select Zip Code", zip_codes)
            filtered_df = df_cannabis_csv[df_cannabis_csv['facility_zip_code'] == selected_zip]

        df_support = filtered_df["equity_program_designation"].value_counts()
    else:
        df_support = df_cannabis_csv["equity_program_designation"].value_counts()

    df_support.index = df_support.index.map({'Y': 'Yes', 'N': 'No'})
    df_support.name = ""

    fig, ax = plt.subplots()
    explode_length = len(df_support)
    explode = (0.1,) * explode_length

    colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightgray']  # Add more colors if needed
    df_support.plot(kind='pie', autopct='%1.1f%%', startangle=90, explode=explode[:explode_length],
                    colors=colors[:explode_length], ax=ax)
    ax.set_title('Equity Program Designation Distribution', fontsize=16)
    ax.legend(df_support.index, title="Designation", loc="best")
    st.pyplot(fig)

    pivot_table = pd.pivot_table(df_cannabis_csv,
                                 values='app_business_name',
                                 index='app_license_category',
                                 columns='equity_program_designation',
                                 aggfunc='count',
                                 fill_value=0)
    st.write(pivot_table)

    # Question 3

    st.header(" 3)Distribution Analysis of Cannabis Facilities by Zip Code")

    def categorize_business(name):
        if 'LLC' in name.upper():
            return 'LLC'
        elif 'CORP' in name.upper() or 'CORPORATION' in name.upper():
            return 'Corp'
        elif 'INC' in name.upper():
            return 'Inc'
        else:
            return 'Others'


    df_cannabis_csv['Business Type'] = df_cannabis_csv['app_business_name'].apply(categorize_business)



    business_type_counts = df_cannabis_csv['Business Type'].value_counts()
    st.write(business_type_counts)

    fig, ax = plt.subplots()
    business_type_counts.plot(kind='bar', ax=ax, color=['skyblue', 'lightgreen', 'lightcoral', 'grey'])
    ax.set_title("Cannabis Facilities by Business Type", fontsize=16)
    ax.set_xlabel("Business Type", fontsize=14)
    ax.set_ylabel("Number of Facilities", fontsize=14)
    st.pyplot(fig)

    business_type = st.sidebar.selectbox("3.Select a Business Type", df_cannabis_csv['Business Type'].unique())
    filtered_data = df_cannabis_csv[df_cannabis_csv['Business Type'] == business_type]

    fig, ax = plt.subplots()
    category_counts = filtered_data['facility_zip_code'].value_counts()
    ax.bar(category_counts.index, category_counts.values, color='skyblue')
    ax.set_xlabel('Facility Zip Code')
    ax.set_ylabel('Number of Facilities')
    ax.set_title(f'Distribution of {business_type} Facilities by Zip Code')
    st.pyplot(fig)



    # Question 4
    st.header(" 4)Map of Cannabis Facilities")

    url_list = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Cannabis_leaf.svg/640px-Cannabis_leaf.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Cannabis_Seychelles_Sketch.jpg/640px-Cannabis_Seychelles_Sketch.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/Cannabis_Leaf.jpg/640px-Cannabis_Leaf.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Deus_computer_engineering.png/640px-Deus_computer_engineering.png",
        "https://upload.wikimedia.org/wikipedia/commons/3/3e/Picto-Factory-2.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Cartoon_Courier_Woman_Carrying_A_Package_For_An_Older_Woman.svg/640px-Cartoon_Courier_Woman_Carrying_A_Package_For_An_Older_Woman.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/P_medicine.svg/640px-P_medicine.svg.png"]


    category_list = []
    for c in df_cannabis_csv.app_license_category:
        if c.lower().strip() not in category_list:
            category_list.append(c.lower().strip())

    sub_df_list = []
    for c in category_list:
        sub_df = df_cannabis_csv[df_cannabis_csv["app_license_category"].str.lower().str.strip() == c]
        sub_df_list.append(sub_df)

    layer_list = []
    for i in range(len(sub_df_list)):
        icon_data = {
            "url": url_list[i],
            "width": 100,
            "height": 100,
            "anchorY": 100
        }

        sub_df_list[i]["icon_data"] = None
        for j in sub_df_list[i].index:
            sub_df_list[i]["icon_data"][j] = icon_data

        icon_layer = pdk.Layer(
            type="IconLayer",
            data=sub_df_list[i],
            get_icon="icon_data",
            get_position='[lon, lat]',
            get_size=4,
            size_scale=10,
            pickable=True
        )
        layer_list.append(icon_layer)
    tool_tip = {
        "html": "Attraction Name:<br/> <b>{app_business_name}</b> <br/> Category: <b>{app_license_category}</b>",
        "style": {"backgroundColor": "orange", "color": "white"}
    }
    view_state = pdk.ViewState(
        latitude=df_cannabis_csv["lat"].mean(),
        longitude=df_cannabis_csv["lon"].mean(),
        zoom=11,
        pitch=0
    )

    category_list.insert(0, "All")
    selected_category = st.sidebar.selectbox(" 4.Please select a category", category_list)

    for i in range(len(category_list)):
        if selected_category == category_list[i]:
            if i == 0:
                map = pdk.Deck(
                    map_style='mapbox://styles/mapbox/outdoors-v11',
                    initial_view_state=view_state,
                    layers=layer_list,
                    tooltip=tool_tip
                )
            else:
                map = pdk.Deck(
                    map_style='mapbox://styles/mapbox/outdoors-v11',
                    initial_view_state=view_state,
                    layers=[layer_list[i - 1]],
                    tooltip=tool_tip
                )

            st.pydeck_chart(map)

    facility_counts = df_cannabis_csv.groupby('facility_zip_code').agg(
        count=('facility_zip_code', 'size'),
        lat=('lat', 'mean'),
        lon=('lon', 'mean')
    ).reset_index()

    heatmap_layer = pdk.Layer(
        'HeatmapLayer',
        data=facility_counts,
        get_position=['lon', 'lat'],
        get_weight='count',
        radius_pixels=100
    )

    view_state = pdk.ViewState(
        latitude=facility_counts["lat"].mean(),
        longitude=facility_counts["lon"].mean(),
        zoom=10
    )

    st.pydeck_chart(pdk.Deck(layers=[heatmap_layer], initial_view_state=view_state))
    def extreme_facilities(df, lat_column, lon_column):
        northernmost = df.loc[df[lat_column].idxmax()]
        southernmost = df.loc[df[lat_column].idxmin()]
        easternmost = df.loc[df[lon_column].idxmax()]
        westernmost = df.loc[df[lon_column].idxmin()]
        return northernmost, southernmost, easternmost, westernmost


    northernmost, southernmost, easternmost, westernmost = extreme_facilities(df_cannabis_csv, 'lat', 'lon')

    st.subheader("Extreme Facilities Analysis")
    st.write("Northernmost Facility:")
    st.write(northernmost)

    st.write("Southernmost Facility:")
    st.write(southernmost)

    st.write("Easternmost Facility:")
    st.write(easternmost)

    st.write("Westernmost Facility:")
    st.write(westernmost)



with tab2:
    retail_df = df_cannabis_csv[df_cannabis_csv['app_license_category'] == 'Retail']
    unique_zip_codes = retail_df['facility_zip_code'].unique()

    selected_zip_code = st.selectbox("Select a Zip Code:", unique_zip_codes)

    if selected_zip_code:
        selected_facilities = retail_df[retail_df['facility_zip_code'] == selected_zip_code]
        display_df = selected_facilities[['app_business_name', 'facility_address']]
        st.table(display_df)

    zip_code_range = st.slider(
        "Select a range of Zip Codes:",
        min_value=int(retail_df['facility_zip_code'].min()),
        max_value=int(retail_df['facility_zip_code'].max()),
        value=(int(retail_df['facility_zip_code'].min()), int(retail_df['facility_zip_code'].max()))
    )

    # Filter dataframe based on selected zip code range
    filtered_df = retail_df[(retail_df['facility_zip_code'] >= zip_code_range[0]) &
                            (retail_df['facility_zip_code'] <= zip_code_range[1])]

    # Create a ScatterplotLayer to display green points
    scatterplot_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered_df,
        get_position="[lon, lat]",
        get_radius=100,  # Radius of the points
        get_color=[0, 255, 0],  # RGB color for green
        pickable=True
    )

    view_state = pdk.ViewState(
        latitude=filtered_df['lat'].mean(),
        longitude=filtered_df['lon'].mean(),
        zoom=11,
        pitch=0
    )

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[scatterplot_layer]
    ))

    unique_business_names = sorted({name for name in df_cannabis_csv['app_business_name'] if pd.notna(name)})

    st.header("Search for a Cannabis Store")

    selected_store = st.selectbox("Choose a Store", unique_business_names)

    if selected_store:
        store_info = df_cannabis_csv[df_cannabis_csv['app_business_name'] == selected_store]
        st.write(store_info)
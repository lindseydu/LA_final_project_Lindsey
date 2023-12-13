import streamlit as st
import pandas as pd
import plotly.express as px
import json

# read the data from a csv file
df = pd.read_csv("2006_-_2012_School_Demographics_and_Accountability_Snapshot.csv")

#data cleaning
# clean white spaces in school names
df['Name'] = df['Name'].str.strip()
df["fl_percent"] = df["fl_percent"].fillna("")
df["frl_percent"] = df["frl_percent"].fillna("")


# combine lunch stipend information
df["free or reduced lunch"] = df['fl_percent'].astype(str) + df['frl_percent'].astype(str)
df['free or reduced lunch'] = df['free or reduced lunch'].str.replace(r'\s+','',regex=True)
df['free or reduced lunch'] = pd.to_numeric(df['free or reduced lunch'], errors='coerce')


# rewrite school year format
def format_school_year(year):
    return f"{year[:4]}-{year[4:]}"
df["schoolyear"] = df["schoolyear"].astype(str).apply(format_school_year)


# organize schools by district
df["district"]=df["DBN"].str[:2]
df["borough"]=df["DBN"].str[2]
letter = df["borough"]=df["DBN"].str[2]


# identify different boroughs
def format_school_location(letter):
    if letter == "M":
        return "Manhattan"
    elif letter == "X":
        return "Bronx"
    elif letter == "K":
        return "Brooklyn"
    elif letter == "R":
        return "Staten Island"
    elif letter == "Q":
        return "Queens"

    else:
        return "Unknown"

# rewrite district format to match geojson file
df["borough"] = df["DBN"].str[2].apply(format_school_location)
df.rename(columns={'district': 'schoolDistrict'}, inplace=True)
df['schoolDistrict'] = df['schoolDistrict'].str.lstrip('0')
df['schoolDistrict'] = df['schoolDistrict'].astype(int)

# st.write(df)


# intro
st.header("Welcome to NYC School Explorer!")
st.write(
    "This interactive data dashboard offers a comprehensive view of the New York City public school demographics from 2006 to 2012. "
    "The dataset is retrieved from the Department of Education. "
    "This visualized dashboard focuses on population distributions by "
     "ethnicity, gender, lunch stipend across all public schools in the city."
    "You can explore total enrollment, lunch stipend, gender and racial distribution across boroughs."
    "You can also investigate information regarding enrollment, race, and gender for each individual school."
)

st.subheader("NYC School District Map")
with open("School Districts.geojson", "r") as read_file:
    nyc_districts_geojson = json.load(read_file)

# Create the Choropleth map
# Create the Choropleth map
fig_intro = px.choropleth_mapbox(df,
                            geojson=nyc_districts_geojson,
                            locations='schoolDistrict',  # This now matches the GeoJSON
                            featureidkey="properties.schoolDistrict",  # Path in GeoJSON
                            color='total_enrollment',  # Data column
                            color_continuous_scale="Viridis",
                            range_color=[0, 6000],
                            mapbox_style="carto-positron",
                            zoom=9, center={"lat": 40.7128, "lon": -74.0100},
                            opacity=0.5,
                            labels={'total_enrollment': 'Total Enrollment'})

# Update layout
fig_intro.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

fig_intro.update_layout(
    coloraxis_colorbar=dict(
        tickvals=[0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000],
        ticktext=['0', '500', '1000', '1500', '2000', '2500', '3000', '3500', '4000', '4500', '5000', '5500', '6000']
    )
)


# Display the figure
st.plotly_chart(fig_intro)


# Q1: What are total enrollment numbers for each borough?
# praparing data
totalM = df[df["borough"] == "Manhattan"]["total_enrollment"].sum()
totalB = df[df["borough"] == "Bronx"]["total_enrollment"].sum()
totalBk = df[df["borough"] == "Brooklyn"]["total_enrollment"].sum()
totalQ = df[df["borough"] == "Queens"]["total_enrollment"].sum()
totalS = df[df["borough"] == "Staten Island"]["total_enrollment"].sum()

st.subheader("Total enrollment number by boroughs")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Manhattan", totalM)
col2.metric("Bronx", totalB)
col3.metric("Brooklyn", totalBk)
col4.metric("Queens", totalQ)
col5.metric("Staten Island", totalS)


# Q2: What are gender distribution looks like across boroughs? How does it contribute to total enrollment?
# preparing data
female_in_M = df[df["borough"] == "Manhattan"]["female_num"].sum()
male_in_M = df[df["borough"]== "Manhattan"]["male_num"].sum()

female_in_B = df[df["borough"] == "Bronx"]["female_num"].sum()
male_in_B = df[df["borough"]== "Bronx"]["male_num"].sum()

female_in_Bk = df[df["borough"] == "Brooklyn"]["female_num"].sum()
male_in_Bk = df[df["borough"]== "Brooklyn"]["male_num"].sum()

female_in_Q = df[df["borough"] == "Queens"]["female_num"].sum()
male_in_Q = df[df["borough"]== "Queens"]["male_num"].sum()

female_in_S = df[df["borough"] == "Staten Island"]["female_num"].sum()
male_in_S = df[df["borough"]== "Staten Island"]["male_num"].sum()

# creating dataframe
enrollment_data = pd.DataFrame({
    "Borough": ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"],
    "Female Enrollment": [female_in_M, female_in_B, female_in_Bk, female_in_Q, female_in_S],
    "Male Enrollment": [-male_in_M, -male_in_B, -male_in_Bk, -male_in_Q, -male_in_S]
})

enrollment_data_melted = enrollment_data.melt(id_vars='Borough', value_vars=['Female Enrollment', 'Male Enrollment'],
                                              var_name='Gender', value_name='Enrollment')

# Map the gender to color
color_discrete_map = {'Female Enrollment': '#FDC500', 'Male Enrollment': '#592E83'}

# Create a bar chart using Plotly
fig_gender = px.bar(enrollment_data_melted,
             x='Borough',
             y='Enrollment',
             color='Gender',
             color_discrete_map=color_discrete_map,
             title="Enrollment by Gender and Borough")

# Display the figure in Streamlit
st.plotly_chart(fig_gender)


# Q3: What is the average free or reduced lunch for schools in each borough?
# preparing data
AveFrl_M = df[df["borough"]=="Manhattan"]["free or reduced lunch"].mean()
AveFrl_B = df[df["borough"]=="Bronx"]["free or reduced lunch"].mean()
AveFrl_Bk = df[df["borough"]=="Brooklyn"]["free or reduced lunch"].mean()
AveFrl_Q = df[df["borough"]=="Queens"]["free or reduced lunch"].mean()
AveFrl_S = df[df["borough"]=="Staten Island"]["free or reduced lunch"].mean()

# creating dataframe
frl_data = pd.DataFrame({
    "Borough": ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"],
    "Free or reduced lunch received": [AveFrl_M, AveFrl_B, AveFrl_Bk, AveFrl_Q, AveFrl_S]
})

# draw the pie chart for lunch stipend
frl_fig = px.pie(frl_data, values='Free or reduced lunch received', names='Borough', title='Average Lunch Stipend by Borough')
frl_fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-1,  # Negative y places the legend below the x-axis
    xanchor="center",
    x=0.5
))


# Q4: What does race distribution looks like across borough?
# preparing data
# students in Manhattan
TotalAsianM = df[df["borough"]=="Manhattan"]["asian_num"].sum()
TotalBlackM = df[df["borough"]=="Manhattan"]["black_num"].sum()
TotalHispanicM = df[df["borough"]=="Manhattan"]["hispanic_num"].sum()
TotalWhiteM = df[df["borough"]=="Manhattan"]["white_num"].sum()

# Students in Bronx
TotalAsianB = df[df["borough"]=="Bronx"]["asian_num"].sum()
TotalBlackB = df[df["borough"]=="Bronx"]["black_num"].sum()
TotalHispanicB = df[df["borough"]=="Bronx"]["hispanic_num"].sum()
TotalWhiteB = df[df["borough"]=="Bronx"]["white_num"].sum()

# Students in Brooklyn
TotalAsianBk = df[df["borough"]=="Brooklyn"]["asian_num"].sum()
TotalBlackBk = df[df["borough"]=="Brooklyn"]["black_num"].sum()
TotalHispanicBk = df[df["borough"]=="Brooklyn"]["hispanic_num"].sum()
TotalWhiteBk = df[df["borough"]=="Brooklyn"]["white_num"].sum()

# Students in Queens
TotalAsianQ = df[df["borough"]=="Queens"]["asian_num"].sum()
TotalBlackQ = df[df["borough"]=="Queens"]["black_num"].sum()
TotalHispanicQ = df[df["borough"]=="Queens"]["hispanic_num"].sum()
TotalWhiteQ = df[df["borough"]=="Queens"]["white_num"].sum()

# Students in Staten Island
TotalAsianS = df[df["borough"]=="Staten Island"]["asian_num"].sum()
TotalBlackS = df[df["borough"]=="Staten Island"]["black_num"].sum()
TotalHispanicS = df[df["borough"]=="Staten Island"]["hispanic_num"].sum()
TotalWhiteS = df[df["borough"]=="Staten Island"]["white_num"].sum()

# creating dataframe
race = pd.DataFrame({
    "Borough": ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"],
    "Asian American Enrollment": [TotalAsianM,TotalAsianB,TotalAsianBk,TotalAsianQ,TotalAsianS],
    "African American Enrollment": [TotalBlackM, TotalBlackB, TotalBlackBk, TotalBlackQ, TotalBlackS],
    "Caucasian American Enrollment": [TotalWhiteM, TotalWhiteB, TotalWhiteBk, TotalWhiteQ, TotalWhiteS],
    "Hispanic American Enrollment": [TotalHispanicM, TotalHispanicB, TotalHispanicBk, TotalHispanicQ, TotalHispanicS]

})
race_melted = race.melt(id_vars='Borough', value_vars=["Asian American Enrollment","African American Enrollment","Caucasian American Enrollment","Hispanic American Enrollment"],
                                              var_name='Race', value_name='Enrollment')

# draw bar chart according to different race and students
race_fig = px.bar(race_melted,
             x='Borough',
             y='Enrollment',
             color='Race',
             title="Enrollment by Race and Borough")

# update layout
race_fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-1,  # Negative y places the legend below the x-axis
    xanchor="center",
    x=0.5
))


# st.plotly_chart(race_fig)

col1,col2=st.columns(2)
with col1:
    st.plotly_chart(frl_fig, use_container_width=True)
with col2:
    st.plotly_chart(race_fig, use_container_width=True)

# Q6: What is the enrollment difference between schools?
enrollment_trend = df.groupby(["Name","schoolyear"])["total_enrollment"].sum()

# st.write(enrollment_trend)
plot_enrollment = enrollment_trend.reset_index()

# creating the sidebar filter

st.sidebar.subheader("Select multiple school to compare enrollment trends:")
select_school = st.sidebar.multiselect("", plot_enrollment['Name'].unique())
st.sidebar.divider()

# Show the plot
if select_school:
    filtered_df = plot_enrollment[plot_enrollment['Name'].isin(select_school)]
    fig = px.line(filtered_df, x="schoolyear", y="total_enrollment", color='Name',
                  labels={'total_enrollment': 'Total Enrollment', 'Name': 'School Name'},
                  title='School Enrollment Trends Comparison')

    # Update the x-axis range here, before displaying the figure
    fig.update_xaxes(range=["2005-2006", "2011-2012"])

    # Now display the updated figure
    st.plotly_chart(fig)


else:
    st.divider()
    st.write("On the side bar, Please select multiple school to compare enrollment trends.")

st.divider()

# Q5: Investigating each individual school
# creating sidebar school filter
# select schools to investigte based on boroughs and districts
# Dropdown to select borough
st.sidebar.header("Investigate by Individual School")
selected_borough = st.sidebar.selectbox('Select a Borough', df['borough'].unique())

# Filter DataFrame based on selected borough
filtered_df_by_borough = df[df['borough'] == selected_borough]

# select district within the selected borough
selected_district = st.sidebar.selectbox('Select a District', filtered_df_by_borough['schoolDistrict'].unique())

# Filter DataFrame based on selected district
filtered_df_by_district = filtered_df_by_borough[filtered_df_by_borough['schoolDistrict'] == selected_district]

# Dropdown to select school within the selected district
selected_school = st.sidebar.selectbox('Select a School', filtered_df_by_district['Name'].unique())


# Mapping selected school to dataframe and sum up enrollment info
school_data = df[df['Name'] == selected_school]
total_enrollment = school_data["total_enrollment"].sum()

# Q5.2: What is the enrollment difference btw 2005 and 2012?
enrollment_2011_2012 = school_data[school_data['schoolyear'] == '2011-2012']['total_enrollment'].sum()
enrollment_2005_2006 = school_data[school_data['schoolyear'] == '2005-2006']['total_enrollment'].sum()
enrollment_difference = enrollment_2011_2012 - enrollment_2005_2006


# Q5.1: What grade are offered in each school?
gradeOffered = []
for grade in ['prek', 'k', 'grade1', 'grade2', 'grade3', 'grade4', 'grade5', 'grade6', 'grade7', 'grade8', 'grade9',
              'grade10', 'grade11', 'grade12']:
    # clean grade data
    school_data[grade] = pd.to_numeric(school_data[grade], errors='coerce').fillna(0)

    # create if condition
    if grade in school_data.columns and school_data[grade].sum() > 0:
        gradeOffered.append(grade.capitalize())

# Convert the list of grades to a string for displaying
gradeOffered_str = ', '.join(gradeOffered)


# creating the interface metric for individual school
st.header("School Details")
st.subheader(f"{selected_school}")
col1, col2 = st.columns(2)
col1.metric("Total enrollment from 2005-2012", f"{total_enrollment}", f"{enrollment_difference}")

# change style
col2.markdown(
    f"<div style='text-align: center;'><span style='font-size: 0.75em;'>Offering</span><br/><span style='font-size: 0.75em;'>{gradeOffered_str}</span></div>",
    unsafe_allow_html=True
)

#Q5.3: What is the enrollment trend for a specific school?
fig_total_enrollment = px.line(school_data, x='schoolyear', y='total_enrollment',
              title=f'Enrollment Trend for {selected_school}',
              labels={'total_enrollment': 'Total Enrollment', 'schoolyear': 'School Year'})

st.plotly_chart(fig_total_enrollment)


# creating the radio button for demographics choice
demo_choice = st.sidebar.radio("Investigate Demographics", ["Race", "Gender"])


# racial distribution for each school
if demo_choice == "Race":
    race_enrollment_trend = school_data.groupby("schoolyear").agg(
        {
        'asian_num': 'sum',
        'black_num': 'sum',
        'white_num': 'sum',
        'hispanic_num': 'sum'
        }
    ).reset_index()

# change format
    race_enrollment_trend.rename(columns={
    'asian_num': 'Asian American',
    'black_num': 'African American',
    'white_num': 'Caucasian American',
    'hispanic_num': 'Hispanic American'
    }, inplace=True)

# melt dataframe to "long" format to draw the chart
    school_data_melted = race_enrollment_trend.melt(id_vars='schoolyear',
                                         value_vars=['Asian American', 'African American', 'Caucasian American', 'Hispanic American'],
                                         var_name='Race', value_name='Enrollment')

# Create an area chart
    fig_race = px.area(school_data_melted, x="schoolyear", y="Enrollment", color="Race",
                   line_group="Race",title=f'Racial Distribution for {selected_school}'
                   )
    fig_race.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=-0.3,  # Negative y places the legend below the x-axis
    xanchor="center",
    x=0.5
    ))
    st.plotly_chart(fig_race)


# gender distribution for each school
elif demo_choice == "Gender":
    total_female = school_data['female_num'].sum()
    total_male = school_data['male_num'].sum()

# Create a DataFrame for the gender distribution
    gender_distribution = pd.DataFrame({
    'Gender': ['Female', 'Male'],
    'Count': [total_female, total_male]
    })

# Create a pie chart
    color_discrete_map = {'Female': '#FDC500', 'Male': '#592E83'}
    fig_gender_pie = px.pie(gender_distribution, names='Gender', values='Count',
                            color = "Gender",
                            color_discrete_map=color_discrete_map,
                            title=f'Gender Distribution in {selected_school}')
    st.plotly_chart(fig_gender_pie)

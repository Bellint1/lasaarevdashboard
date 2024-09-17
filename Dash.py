import streamlit as st
import plotly.express as px
import pandas as pd
import pyodbc
from PIL import Image
import warnings
warnings.filterwarnings("ignore",)
from pyodbc import OperationalError

st.set_page_config(page_title="LASAA Report", page_icon=":bar_chart:",layout="wide")

sidebar_style = """
<style>
[data-testid="stSidebar"] {
    background-image: url(https://lasaa.lg.gov.ng/images/lasaa-web-logo1.png);
    background-size: 200px;
    background-repeat: no-repeat;
    background-position: 10px 20px;
}
</style>
"""

st.markdown(sidebar_style, unsafe_allow_html=True)


hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    footer:after {
        content:'Copyrigt LASAA 2024';
        visibility: visible;
        display: block;
        position: relative;
        padding: 5px;
        top: 2px;
    }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
image = Image.open('lasaa-web-logo1.png')
custom_css = """
    <style>
    @media (min-width: 900px) {
        .logo-container {
            display: none;
        }
    }
    @media (max-width: 900px) {
        .logo-container {
            display: block;
        }
    }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)



@st.cache_resource
def init_connection():
    try:
        connection =pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=" + st.secrets["database"]["server"] + ";"
            "DATABASE=" + st.secrets["database"]["database"] + ";"
            "UID=" + st.secrets["database"]["username"] + ";"
            "PWD=" + st.secrets["database"]["password"]
        )
        return connection
    except OperationalError as e:
        st.error("Failed to connect to the database. Please try again or contact Administrator @SAuto.")
        st.error(f"Error details: {e}")
        return None

conn = init_connection()

def read_query_from_file(file_path):
    with open(file_path, 'r') as file:
        query = file.read()
    return query

# Function to run a query and fetch data
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        columns = [column[0] for column in cur.description]
        rows = cur.fetchall()
        return pd.DataFrame.from_records(rows, columns=columns)

# Define queries
query1 = read_query_from_file('bill.sql')
query2 = read_query_from_file('payment.sql')
query3 = read_query_from_file('customerarrears.sql')

# Fetch data from the database
df = run_query(query1)
df1 = run_query(query2)
df2 = run_query(query3)




df.loc[df['CustomerType'] == 'Practitioner', 'LGACode'] = '3P'
# st.dataframe(df)
LGA_group = {
    'GGE': 'Lagos West1','FKJ': 'Lagos West1','LSD': 'Lagos West1','MUS': 'Lagos West1',
    'CVM': 'Lagos West1','OGB': 'Lagos West1','KJA': 'Lagos West1','JJJ': 'Lagos West2',
    'AMO': 'Lagos West2','AGL': 'Lagos West2','BDG': 'Lagos West2','KTU': 'Lagos West2',
    'MOK': 'Lagos West2','KRD': 'Lagos East','KSF': 'Lagos East','MAS': 'Lagos East',
    'EPE': 'Lagos West1', 'SMK': 'Lagos East','AKD': 'Lagos East','LND': 'Lagos Central','LSR': 'Lagos Central',
    'APP': 'Lagos Central','EKY': 'Lagos Central','IKB': 'Lagos Central','LKP': 'Lagos Central',
    'ITK': 'Lagos Central','LGI': 'Lagos Central', 'INS': 'Institution'
}
df['Region'] = df['LGACode'].map(LGA_group)
df1['Region'] = df1['LGACode'].map(LGA_group)
df2['Region'] = df2['LGACode'].map(LGA_group)

col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image(image,width=200)
    
html_title = """
    <style>
        .title-test {
            font-weight: bold;
            padding: 5px;
            border-radius: 6px;
            text-align: center;
        }

        /* Media Queries for Responsiveness */
        @media (max-width: 600px) {
            .title-test {
                font-size: 20px;
                padding: 3px;
            }
        }

        @media (min-width: 601px) and (max-width: 1024px) {
            .title-test {
                font-size: 24px;
                padding: 4px;
            }
        }

        @media (min-width: 1025px) {
            .title-test {
                font-size: 28px;
                padding: 5px;
            }
        }
    </style>
    <h1 class="title-test">2024 Revenue Report</h1>
"""
with col2:
    st.markdown(html_title, unsafe_allow_html=True)
    
customer_types = list(df['CustomerType'].unique())
first_party = {customer_type: ['All']+ list(df[df['CustomerType'] == customer_type]['Region'].unique()) for customer_type in customer_types}
first_party['All'] = ['All'] + list(df['Region'].unique())
customer_types.insert(0, 'All')


with st.container():    
    customertype = st.sidebar.selectbox("Select Customer Type", options=customer_types)
    if customertype == 'Business Owner':
        selected_subtype = st.sidebar.selectbox("LGA Regions", options=first_party[customertype])
        
    if customertype == 'All':
        df_selection = df
    else:
        df_selection = df.query("CustomerType == @customertype")
    # st.write(df)
if df_selection.empty:
    st.warning("No data available based on the current filter!")
    st.stop()
    
if customertype == 'All':
    df1_selection = df1
else:
    df1_selection = df1.query("CustomerType == @customertype")

if df1_selection.empty:
    st.warning("No data available for the selected year!")
    st.stop()
    
if customertype == 'All':
    df2_selection = df2
else:
    df2_selection = df2.query("CustomerType == @customertype")

if df2_selection.empty:
    st.warning("No data available for the selected year!")
    st.stop()



total_signage_cost_by_group = df_selection.groupby(['Region'])['TotalCost'].sum().reset_index()
total_Amountpaid_by_group = df1_selection.groupby(['Region'])['AmountPaid'].sum().reset_index()
# signage_cost_ins = df_selection.groupby('LGACode')['TotalCost'].sum().reset_index()
# total_Amountpaid_ins = df1_selection.groupby('LGACode')['AmountPaid'].sum().reset_index()
# ins_totalcost = signage_cost_ins [signage_cost_ins['LGACode'] == 'INS']
# ins_amountpaid = total_Amountpaid_ins [total_Amountpaid_ins['LGACode'] == 'INS']
# total_signage_cost_by_group.columns = ['Region', 'Revenue']
bill_generated = df_selection['RequestId'].count()
bill_worth = df_selection['TotalCost'].sum()
ren_bill = df_selection.groupby('Application Type')['RequestId'].count()
ren_bill_worth = df_selection.groupby('Application Type')['TotalCost'].sum()
bill_gen_lga = df_selection.groupby('LGACode')['TotalCost'].sum()
act_rev_lga = df1_selection.groupby('LGACode')['AmountPaid'].sum()
act_rev = df1_selection['AmountPaid'].sum()
unique_arreas = df_selection.drop_duplicates(subset='CustomerID', keep='first')
unique_arrea= unique_arreas['CustomerArrears'].sum()
cust_bal = df2_selection['CustomerArrears'].sum()
total_arrears= cust_bal - bill_worth 
total_arreas_by_lga =unique_arreas.groupby('LGACode')['CustomerArrears'].sum().reset_index()
total_arreas_by_group =unique_arreas.groupby('Region')['CustomerArrears'].sum().reset_index()
unique_payment = df1_selection.groupby('CustomerName')['AmountPaid'].sum().reset_index()
first_party_target_rev = 3325000000
target_rev= {'Lagos Central' : 490000000,
             'Lagos West1' : 490000000, 
             'Lagos West2' : 190000000, 
             'Lagos East' : 355000000,
             'Institution' : 1800000000 }


df1_selection['PaymentDate'] = pd.to_datetime(df1_selection['PaymentDate'])
df_selection['Month'] = df_selection['Timestamp'].dt.to_period('M')
df1_selection['Month'] =(df1_selection['PaymentDate'].dt.to_period('M'))
bills_by_month = df_selection.groupby(['Month', 'Application Type']).agg({'RequestId': 'count', 'TotalCost': 'sum'}).reset_index()
bills_by_month_group = df_selection.groupby(['Month', 'Application Type', 'Region']).agg({'RequestId': 'count', 'TotalCost': 'sum'}).reset_index()
rev_by_month = df1_selection.groupby('Month')['AmountPaid'].sum().reset_index()
rev_by_month_group = df1_selection.groupby(['Month', 'Region'])['AmountPaid'].sum().reset_index()
bills_by_month['Month'] = bills_by_month['Month'].dt.strftime('%B')
rev_by_month['Month'] = rev_by_month['Month'].dt.strftime('%B')
bills_by_month_group['Month'] = bills_by_month_group['Month'].dt.strftime('%B')
rev_by_month_group['Month'] = rev_by_month_group['Month'].dt.strftime('%B')
month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
rev_by_month['Month'] = pd.Categorical(rev_by_month['Month'], categories=month_order, ordered=True)
bills_by_month['Month'] = pd.Categorical(bills_by_month['Month'], categories=month_order, ordered=True)
rev_by_month_group['Month'] = pd.Categorical(rev_by_month_group['Month'], categories=month_order, ordered=True)
bills_by_month_group['Month'] = pd.Categorical(bills_by_month_group['Month'], categories=month_order, ordered=True)
bills_by_month = bills_by_month.sort_values('Month')
rev_by_month = rev_by_month.sort_values('Month')
bills_by_month_group = bills_by_month_group.sort_values('Month')
rev_by_month_group = rev_by_month_group.sort_values('Month')

# aligned_lga_codes = bill_gen_lga.index.union(act_rev_lga.index)
# bill_gen_lga = bill_gen_lga.reindex(aligned_lga_codes, fill_value=0)
# act_rev_lga = act_rev_lga.reindex(aligned_lga_codes, fill_value=0)



def format_value(value, currency=False):
    if currency:
        return f"₦ {value:,.2f}"
    return f"{value:,.2f}"

metric_style = """
<style>
.metric-box {
    background-color: #0E1117;
    border: 1px solid #CCCCCC;
    padding: 5% 5% 5% 10%;
    border-radius: 5px;
    border-left: 0.5rem solid #9AD8E1 !important;
    box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;
    text-align: center;  /* Center align the text */
}
.metric-box div {
    font-size: 1.5rem;
    font-weight: 600;
    color:  #F1F1F1;
}
.metric-box .value {
    font-size: 2.5rem;
    font-weight: 700;
}
</style>
"""

st.markdown(metric_style, unsafe_allow_html=True)

def render_metric(label, value, col):
    col.markdown(f"""
    <div class="metric-box">
        <div style="font-size: 1rem; font-weight: 600;">{label}</div>
        <div style="font-size: 2rem; font-weight: 700;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2 =st.columns(2)
if customertype == 'All':
    with col1:
        render_metric("Total Bill Generated (Current Charge)", format_value(bill_worth, currency=True), col1)
    
    with col2:
        render_metric("Total Arrears", format_value(total_arrears, currency=True), col2)
elif customertype == 'Business Owner':
     if selected_subtype == 'All':
         with col1:
            render_metric("Total Bill Generated (Current Charge)", format_value(bill_worth, currency=True), col1)
         with col2:
            render_metric("Total Arrears", format_value(total_arrears, currency=True), col2)
     else:
         for index, row in total_signage_cost_by_group.iterrows():
            if row['Region'] == selected_subtype:
                group = row['Region']
                cost = row['TotalCost']
                with col1:
                    render_metric(f"Total Bill Generated for {group} (Current Charge)", format_value(cost, currency=True), col1)
         for index, row in total_arreas_by_group.iterrows():
            if row['Region'] == selected_subtype:
                group = row['Region']
                cost = row['CustomerArrears']
                with col2:
                    render_metric(f"Total Arrears for {group}", format_value(cost, currency=True), col2)
        
else:
    with col1:
        render_metric("Total Bill Generated (Current Charge)", format_value(bill_worth, currency=True), col1)
    
    with col2:
        render_metric("Total Arrears", format_value(total_arrears, currency=True), col2)
    
metric_style = """
<style>
.metric-box {
    background-color: #0E1117;
    border: 1px solid #CCCCCC;
    padding: 5% 5% 5% 10%;
    border-radius: 5px;
    border-left: 0.5rem solid #9AD8E1 !important;
    box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;
    text-align: center;  /* Center align the text */
}
.metric-box div {
    font-size: 1.5rem;
    font-weight: 600;
    color:  #F1F1F1;
}
.metric-box .value {
    font-size: 2.5rem;
    font-weight: 700;
}
</style>
"""

st.markdown(metric_style, unsafe_allow_html=True)


  
col1, col2 =st.columns(2)
if customertype == 'All':
    st.write()
elif customertype == 'Business Owner':
    if selected_subtype == 'All':
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div   div style="font-size: 1rem; font-weight: 600;">Target Revenue</div>
                <div style="font-size: 2rem; font-weight: 700;">{format_value(first_party_target_rev, currency=True)}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        if selected_subtype in target_rev:
            cost = target_rev[selected_subtype]
            with col1:
                st.markdown(f"""
                <div class="metric-box">
                    <div style="font-size: 1rem; font-weight: 600;">Target Revenue for {group}</div>
                    <div style="font-size: 2rem; font-weight: 700;">{format_value(cost, currency=True)}</div>
                </div>
                """, unsafe_allow_html=True)
        
else:
    st.write()


col4, col5, col6 = st.columns([1, 4, 1])


if customertype == 'All':
    with col5:
        st.markdown(f"""
        <div class="metric-box">
            <div style="font-size: 1rem; font-weight: 600;">Total Revenue</div>
            <div style="font-size: 2rem; font-weight: 700;">{format_value(act_rev, currency=True)}</div>
        </div>
        """, unsafe_allow_html=True)
elif customertype == 'Business Owner':
    if selected_subtype == 'All':
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div   div style="font-size: 1rem; font-weight: 600;">Total Revenue</div>
                <div style="font-size: 2rem; font-weight: 700;">{format_value(act_rev, currency=True)}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        for index, paid in total_Amountpaid_by_group.iterrows():
            if paid['Region'] == selected_subtype:
                group_name = paid['Region']
                Amount = paid['AmountPaid']
                with col2:
                    st.markdown(f"""
                <div class="metric-box">
                    <div style="font-size: 1rem; font-weight: 600;">Total Revenue for {group_name}</div>
                    <div style="font-size: 2rem; font-weight: 700;">{format_value(Amount, currency=True)}</div>
                </div>
                """, unsafe_allow_html=True)
        
else:
    with col5:
        st.markdown(f"""
        <div class="metric-box">
            <div style="font-size: 1rem; font-weight: 600;">Total Revenue</div>
            <div style="font-size: 2rem; font-weight: 700;">{format_value(act_rev, currency=True)}</div>
        </div>
        """, unsafe_allow_html=True)
    
fig = px.bar(rev_by_month, x='Month', y='AmountPaid', text = rev_by_month['AmountPaid'].apply(lambda x: f'₦{x / 1_000_000:,.2f}M'),
             title='Revenue Generated by Month', labels={'AmountPaid': 'Actual Revenue', 'Month': 'Month'}, 
             hover_data={'AmountPaid': ':,.0f'}, category_orders={'Month': month_order})


graph_style = """
<style>
.graph-container {
    background-color: #0E1117;
    border: 1px solid #CCCCCC;
    padding: 5% 5% 5% 10%;
    border-radius: 5px;
    border-left: 0.5rem solid #9AD8E1 !important;
    box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;
    margin: 0 auto;  /* Center the container */
    width: 80%;  /* Adjust width as needed */
    text-align: center;
}
</style>
"""
col1, col2, col3 = st.columns([1, 4, 1])

if customertype == "All":
    with col2:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    

elif customertype == "Business Owner":
    if selected_subtype == 'All':
        with col2:
            st.markdown('<div class="graph-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        rev_by_month_group = rev_by_month_group[rev_by_month_group['Region'] == selected_subtype]

        if not rev_by_month_group.empty:  
            fig1 = px.bar(
            rev_by_month_group,
            x='Month',
            y='AmountPaid',
            text=rev_by_month_group['AmountPaid'].apply(lambda x: f'₦{x / 1_000_000:,.2f}M'),
            title=f'Revenue Generated by Month in {selected_subtype}',  
            labels={'AmountPaid': 'Actual Revenue', 'Month': 'Month'},
            hover_data={'AmountPaid': ':,.0f'},
            category_orders={'Month': month_order} 
        )
            with col2:
                st.markdown('<div class="graph-container">', unsafe_allow_html=True)
                st.plotly_chart(fig1, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
    
else:
    with col2:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

bills_by_month_newapps = bills_by_month[bills_by_month['Application Type'] == 'New Applications'].reset_index(drop = True)  
bills_by_month_group_newapps = bills_by_month_group[bills_by_month_group['Application Type'] == 'New Applications'].reset_index(drop = True) 
  
fig = px.bar(bills_by_month_newapps, x='Month', y='RequestId', text = bills_by_month_newapps['TotalCost'].apply(lambda x: f'₦{x / 1_000_000:,.2f}M'),
             title='Bills Generated by Month',labels={'RequestId': 'Number of Bills', 'Month': 'Month'}, hover_data={'TotalCost': ':,.0f'},
             category_orders={'Month': month_order})



col1, col2, col3 = st.columns([1, 4, 1])
if customertype == 'All':
    with col2:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        
elif customertype == 'Business Owner':
    if selected_subtype == 'All':
        with col2:
            st.markdown('<div class="graph-container">', unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        bills_by_month_group1 = bills_by_month_group_newapps[bills_by_month_group_newapps['Region'] == selected_subtype]

        if not bills_by_month_group1.empty:  
            fig2 = px.bar(
            bills_by_month_group1,
            x='Month',
            y='RequestId',
            text=bills_by_month_group1['TotalCost'].apply(lambda x: f'₦{x / 1_000_000:,.2f}M'),
            title=f'Bills Generated by Month in {selected_subtype}',  
            labels={'RequestId': 'Number of Bills', 'Month': 'Month'},
            hover_data={'TotalCost': ':,.0f'},
            category_orders={'Month': month_order} 
        )
            st.markdown('<div class="graph-container">', unsafe_allow_html=True)
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

else:
    with col2:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

total_arreas_by_lga_cust =unique_arreas[['CustomerName', 'CustomerArrears']].reset_index(drop=True)
unique_payment_cust = unique_payment[['CustomerName', 'AmountPaid']].reset_index(drop=True)

merged_df = pd.merge(total_arreas_by_lga_cust, unique_payment_cust, on='CustomerName', how='outer')
merged_df.fillna({'CustomerArrears': 0, 'AmountPaid': 0}, inplace=True)


col1, col2, col3 = st.columns([1, 4, 1])
if customertype == 'All':
    st.write()
        
elif customertype == 'Business Owner':
    if selected_subtype == 'All':
        st.write()
    else:
        st.write()

else:
    with col2:
        sort_column = st.selectbox("Sort by:", ["CustomerArrears", "AmountPaid"])
        sort_order = st.radio("Order:", ("Ascending", "Descending"))
        ascending_order = True if sort_order == "Ascending" else False
        merged_df = merged_df.sort_values(by=sort_column, ascending=ascending_order).reset_index(drop=True)

        merged_df['CustomerArrears'] = merged_df['CustomerArrears'].apply(lambda x: f'₦{x:,.2f}')
        merged_df['AmountPaid'] = merged_df['AmountPaid'].apply(lambda x: f'₦{x:,.2f}')



        styled_df = merged_df.style.set_properties(**{
            'background-color': '#f0f0f0',
            'color': 'black',
            'border-color': 'black',
            'border-style': 'solid',
            'border-width': '1px',
            'text-align': 'center'
        }).set_table_styles([{
            'selector': 'th',
            'props': [('font-size', '12pt'),
                ('font-weight', 'bold'),
                ('color', 'black'),
                ('background-color', '#BFC9CA')]
        }])

        html_table = styled_df.render()
        st.markdown(html_table, unsafe_allow_html=True)
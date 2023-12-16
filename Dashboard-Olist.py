# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 11:47:58 2023

@author: Albertus Bagus

how to run it?

1. Open Anaconda Powershell Prompt
2. Ketikkan 2 baris di bawah ini
conda activate main-ds
streamlit run Dashboard-Olist.py

"""
# Menyiapkan Library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='whitegrid')

# Menyiapkan Fungsi untuk DataFrame
def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_delivered_customer_date').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_tren(df):
    tren = df.groupby(by="delivered_month").agg({
        'order_id':'nunique'
        }).reset_index().sort_index()
    return tren

def create_del_cat(df):
    del_cat = df.groupby(by='delivered_time_cat').agg({
        'order_id':'nunique'
        }).reset_index().sort_values(by='order_id', ascending=False)
    return del_cat

def create_estimated_cat(df):
    estimated_cat = df.groupby(by='est_cat').agg({
        'order_id':'nunique'
        }).reset_index().sort_values(by='order_id', ascending=False)
    return estimated_cat

def create_favorite_category(df):
    favorite_category = df.groupby(by='product_category_name_english').agg({
        'order_id':'nunique'
    }).reset_index().sort_values(by='order_id',ascending=False)
    return favorite_category

def create_fav_cat(df):
    fav_cat = df.groupby(['year_month', 'product_category_name_english']).agg({
        'order_id':'nunique'
    }).reset_index().sort_values(by='order_id',ascending=False)
    fav_cat = fav_cat.sort_values(['year_month', 'order_id'], ascending=[True, False])
    fav_cat = fav_cat.drop_duplicates(subset='year_month')
    return fav_cat

def create_favorite_payment(df):
    favorite_payment = df.groupby(by='payment_type').agg({
        'order_id':'nunique',
        'payment_value':'sum'
    }).reset_index().sort_values(by='order_id',ascending=False)
    return favorite_payment

def create_fav_pay(df):
    fav_pay = df.groupby(['year_month', 'payment_type']).agg({
        'order_id':'nunique'
    }).reset_index().sort_values(by='order_id',ascending=False)
    fav_pay = fav_pay.sort_values(['year_month', 'order_id'], ascending=[True, False])
    fav_pay = fav_pay.drop_duplicates(subset='year_month')
    return fav_pay

def create_review(df):
    review = df.groupby(by='review_score').agg({
        'order_id':'nunique'
    }).reset_index().sort_values(by='order_id',ascending=False)
    return review

def create_cat_review(df):
    review = df.groupby('product_category_name_english', as_index=False).agg({
        'review_score':'mean',
        'order_id':'nunique'
    }).sort_values('review_score',ascending=False)
    review = review[review.order_id>100]
    return review

def create_deli_cat(df):
    deli_cat = df.groupby('delivered_time_cat', as_index=False).agg({
        'order_id':'nunique',
        'review_score':'mean'
    }).sort_values('review_score',ascending=False)
    return deli_cat

def create_diff_deli_est(df):
    diff_deli_est = df.groupby('est_cat', as_index=False).agg({
        'order_id':'nunique',
        'review_score':'mean'
    }).sort_values('review_score',ascending=False)
    return diff_deli_est

def create_reviews(df):
    reviews = df[['delivered_time','diff_est_del','review_score']]
    return reviews

# Membuat Komponen Filter
all_df = pd.read_csv("olist_df.csv")

datetime_columns = ["order_delivered_customer_date"]
all_df.sort_values(by="order_delivered_customer_date", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
    
# Membuat Filter

min_date = all_df["order_delivered_customer_date"].min()
max_date = all_df["order_delivered_customer_date"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("olist_store.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Memanggil DataFrame
main_df = all_df[(all_df["order_delivered_customer_date"] >= str(start_date)) & 
                (all_df["order_delivered_customer_date"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
tren = create_tren(main_df)
del_cat = create_del_cat(main_df)
estimated_cat = create_estimated_cat(main_df)
favorite_category = create_favorite_category(main_df)
fav_cat = create_fav_cat(main_df)
favorite_payment = create_favorite_payment(main_df)
fav_pay = create_fav_pay(main_df)
review = create_review(main_df)
cat_review = create_cat_review(main_df)
deli_cat = create_deli_cat(main_df)
diff_deli_est = create_diff_deli_est(main_df)
reviews = create_reviews(main_df)

# Melengkapi Dashboard dengan Berbagai Visualisasi Data
st.header('Proyek Analisis Data: Brazilian E-Commerce Public Dataset by Olist')

## Daily Order & Nilai Pesanan
st.subheader('Daily Orders')
 
col1, col2 = st.columns(2)
 
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Pesanan", value=total_orders)
 
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "BRL", locale='es_CO') 
    st.metric("Total Nilai Transaksi", value=total_revenue)

## Tren Pesanan
st.subheader(f"Pesanan yang Terkirim pada {start_date} hingga {end_date}")

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(tren["delivered_month"],
        tren["order_id"],
        marker='o',
        linewidth=2,
        color="#72BCD4")
ax.set_xlabel("Bulan")
ax.set_xlabel("Jumlah Order")
ax.tick_params(axis='y', labelsize=15)
ax.tick_params(axis='x', labelsize=15, rotation=90)

st.pyplot(fig)

## Proses Pengiriman dari Seller ke Customer
st.subheader(f"Proses Pengiriman dari Seller ke Customer pada {start_date} hingga {end_date}")

fig = plt.figure(figsize=(15, 8))
colors = ("#48cae4","#00b4d8", "#90e0ef","#0096c7",'#0077b6')
explode1 = (0.05, 0.05, 0.05, 0.05, 0.05)
explode2 = (0.05, 0.05, 0.05)

plt.subplot(1, 2, 1)
plt.pie(
    x     =del_cat['order_id'],
    labels=del_cat['delivered_time_cat'],
    autopct='%1.1f%%',
    colors=colors,
    explode=explode1
)
plt.title("Lama Pengiriman Pesanan ke Customer", loc="center", fontsize=17)

plt.subplot(1, 2, 2)
plt.pie(
    x     =estimated_cat['order_id'],
    labels=estimated_cat['est_cat'],
    autopct='%1.1f%%',
    colors=colors,
    explode=explode2
)
plt.title("Selisih Estimasi Waktu dengan Pengiriman Sebenarnya", loc="center", fontsize=17)

st.pyplot(fig)

## Kategori Produk dengan Penjualan Terbanyak dan Tersedikit
st.subheader(f" Kategori Produk dengan Penjualan Terbanyak dan Tersedikit pada {start_date} hingga {end_date}")

fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(20, 25))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="order_id", y="product_category_name_english", data=favorite_category.sort_values(by='order_id',ascending=False).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("5 Kategori dengan Order Terbesar", loc="center", fontsize=25)
ax[0].tick_params(axis ='y', labelsize=20)

sns.barplot(x="order_id", y="product_category_name_english", data=favorite_category.sort_values(by='order_id',ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("5 Kategori dengan Order Terendah", loc="center", fontsize=25)
ax[1].tick_params(axis='y', labelsize=20)

st.pyplot(fig)

## Metode Pembayaran yang Paling banyak Digunakan
st.subheader(f" Metode Pembayaran yang Paling banyak Digunakan pada {start_date} hingga {end_date}")

col1, col2 = st.columns(2)

with col1:
    credit_card = favorite_payment[favorite_payment.payment_type=='credit_card'].iloc[0,[2]]
    st.metric("Credit Card", value=credit_card)

with col2:
    boleto = favorite_payment[favorite_payment.payment_type=='boleto'].iloc[0,[2]]
    st.metric("Boleto", value=boleto)

col3, col4 = st.columns(2)

with col3:
    voucher = favorite_payment[favorite_payment.payment_type=='voucher'].iloc[0,[2]]
    st.metric("Voucher", value=voucher)

with col4:
    debit_card = favorite_payment[favorite_payment.payment_type=='debit_card'].iloc[0,[2]]
    st.metric("Debit Card", value=debit_card)

fig = plt.figure(figsize=(10, 5))
colors = ("#0077b6", "#00b4d8", "#90e0ef", "#caf0f8")
explode = (0.1, 0.1, 0.1, 0.1)

plt.pie(
    x     =favorite_payment['order_id'],
    labels=favorite_payment['payment_type'],
    autopct='%1.1f%%',
    colors=colors,
    explode=explode
)
plt.title('Metode Pembayaran yang Paling banyak Digunakan', loc="center", fontsize=20)

st.pyplot(fig)

## Review
st.subheader(f" Review dari Customer pada {start_date} hingga {end_date}",)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    rating5 = review[review.review_score==5].iloc[0,[1]]
    st.metric(":star::star::star::star::star:", value=rating5)

with col2:
    rating4 = review[review.review_score==4].iloc[0,[1]]
    st.metric(":star::star::star::star:", value=rating4)
    
with col3:
    rating3 = review[review.review_score==3].iloc[0,[1]]
    st.metric(":star::star::star:", value=rating3)

with col4:
    rating2 = review[review.review_score==2].iloc[0,[1]]
    st.metric(":star::star:", value=rating2)
    
with col5:
    rating1 = review[review.review_score==1].iloc[0,[1]]
    st.metric(":star:", value=rating1)    

fig = plt.figure(figsize=(15, 7))

colors = ("#48cae4","#00b4d8", "#90e0ef","#0096c7",'#0077b6')
explode = (0.05,0.05,0.05,0.05,0.05)

plt.pie(
    x     =review['order_id'],
    labels=review['review_score'],
    autopct='%1.1f%%',
    colors=colors,
    explode=explode
)
plt.title('Nilai Review Pesanan yang Diberikan Customer', loc="center", fontsize=12)

st.pyplot(fig)

## Review per Kategori
st.subheader(f" Review per Kategori pada {start_date} hingga {end_date}",)

cat_review = cat_review[cat_review.order_id>100]

fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(20, 25))

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="review_score", y="product_category_name_english", data=cat_review.sort_values(by='review_score',ascending=False ).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("5 Kategori dengan Review Terbesar", loc="center", fontsize=30)
ax[0].tick_params(axis ='y', labelsize=17)

sns.barplot(x="review_score", y="product_category_name_english", data=cat_review.sort_values(by='review_score',ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("5 Kategori dengan Review Terendah", loc="center", fontsize=30)
ax[1].tick_params(axis='y', labelsize=17)

st.pyplot(fig)

## Review Berdasarkan Lama Pengiriman
st.subheader(f" Review Berdasarkan Lama Pengiriman pada {start_date} hingga {end_date}")

fig = plt.figure(figsize=(20, 10))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="review_score", y="delivered_time_cat", data=deli_cat.sort_values(by='review_score',ascending=False ), palette=colors)
plt.title('Review Berdasarkan Lama Pengiriman', fontsize=25)
plt.xlabel('Review Score', fontsize=18)
plt.ylabel('Lama Pengiriman', fontsize=18)
plt.grid(axis = 'x',linestyle = '--', linewidth = 1)

st.pyplot(fig)


## Review Berdasarkan Selisih Estimasi Waktu dengan Pengiriman Sebenarnya
st.subheader(f"Review Berdasarkan Selisih Estimasi Waktu dengan Pengiriman Sebenarnya pada {start_date} hingga {end_date}")

fig = plt.figure(figsize=(20, 10))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="review_score", y="est_cat", data=diff_deli_est.sort_values(by='review_score',ascending=False ), palette=colors)
plt.title('Review Berdasarkan Selisih Estimasi Waktu dengan Pengiriman Sebenarnya', fontsize=25)
plt.xlabel('Review Score')
plt.ylabel('Selisih Estimasi Waktu')
plt.grid(axis = 'x',linestyle = '--', linewidth = 1)

st.pyplot(fig)

## Korelasi Antara Nilai Review dengan Proses Pengiriman
st.subheader(f"Korelasi Antara Nilai Review dengan Proses Pengiriman pada {start_date} hingga {end_date}")

fig = plt.figure(figsize=(15, 8))
dataplot=sns.heatmap(reviews.corr(), cmap="YlGnBu", annot=True)

st.pyplot(fig)

with st.expander("Penjelasan Tabel Korelasi"):
    st.write(
        """
        Korelasi bernilai "+" berarti bahwa jika variabel A naik, maka variabel B juga naik. Begitu pula sebaliknya.
        
        Korelasi bernilai "-" berarti bahwa jika variabel A naik, maka variabel B turun. Begitu pula sebaliknya.
        
        Besar kenaikan atau penurunan masing-masing variabel bergantung pada nilai korelasinya.
        
        Semakin dekat korelasi menuju 1 atau -1, maka kenaikan atau penurunannya semakin besar.
        """
    )
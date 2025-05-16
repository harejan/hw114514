import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

# 從 Streamlit Secrets 讀取 GEE 服務帳戶金鑰 JSON
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]

# 使用 google-auth 進行 GEE 授權
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)

# 初始化 GEE
ee.Initialize(credentials)
###############################################
st.set_page_config(layout="wide")
st.title("😺114514作業streamlit")
# 地理區域
my_point = ee.Geometry.Point([120.5583462887228, 24.081653403304525])
# 擷取 Landsat NDVI
my_image = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterBounds(my_point)
    .filterDate('2021-01-01', '2022-01-01')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
)
vis_params1 = {'min':100, 'max': 3500, 'bands': ['B5', 'B4', 'B3']}

training = my_image.sample(
    **{
        'region': my_image.geometry(),  # 若不指定，則預設為影像my_image的幾何範圍。
        'scale': 10,
        'numPixels': 10000,
        'seed': 0,
        'geometries': True,  # 設為False表示取樣輸出的點將忽略其幾何屬性(即所屬網格的中心點)，無法作為圖層顯示，可節省記憶體。
    }
)
n_clusters = 5
clusterer_KMeans = ee.Clusterer.wekaKMeans(nClusters=n_clusters).train(training)

result = my_image.cluster(clusterer_KMeans)

legend_dict = {
    'one': '#f0e4d4',
    'two': '909fa6',
    'three': '#d18063',
    'four': '#917b56',
    'five': '#d2b5bb',
    'six': '#a2b59f',
    'seven': '#ede1f0',
    'eight': '#ede1e3',
    'nine':'d1dfe8',
    'ten':'#f9d9ca'
}
palette = list(legend_dict.values())
vis_params2 = {'min': 0, 'max': 7, 'palette': palette}

# 顯示地圖
Map = geemap.Map()
Map.add_basemap('HYBRID')
left_layer = geemap.ee_tile_layer(my_image, vis_params1, 'false coler')
right_layer = geemap.ee_tile_layer(result, vis_params2, 'wekakMeans classified land cover')
Map.centerObject(my_image.geometry(), 10)
Map.split_map(left_layer, right_layer)
Map.add_legend(title='Land Cover Type', legend_dict = legend_dict,draggable=False, position = 'bottomright')
Map.to_streamlit(height=800, width=1400)

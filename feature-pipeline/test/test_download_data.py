import hsfs
connection = hsfs.connection()
fs = connection.get_feature_store(name='energyconsumption_featurestore')
fg = fs.get_feature_group('nyc_green_taxi', version=1)

print(fg)
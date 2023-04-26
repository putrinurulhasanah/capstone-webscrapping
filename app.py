from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
jobs = []

for i in range(0,16):
    url = f"https://www.kalibrr.id/id-ID/job-board/te/data/{i}"
    response = requests.get(url)
    response = response.content
    soup = BeautifulSoup(response, 'html.parser')
    table = soup.find('div', attrs={'class':'k-border-b k-border-t k-border-tertiary-ghost-color md:k-border md:k-overflow-hidden md:k-rounded-lg'})
    rows = table.find_all('div', attrs={'class':'k-grid k-border-tertiary-ghost-color k-text-sm k-p-4 md:k-p-6 css-1b4vug6'})
    for row in rows:
        title = row.find('a', attrs={'class':'k-text-primary-color'}).text
        location = row.find('a', attrs={'class':'k-text-subdued k-block'}).text
        posted_deadline = row.find('span', attrs={'class':'k-block k-mb-1'}).text
        company = row.find_all('a', attrs={'class':'k-text-subdued'})[1].text
        jobs.append([title, location, posted_deadline, company])

#change into dataframe
df_jobs = pd.DataFrame(jobs, columns=['title', 'location', 'posted_deadline', 'company'])

#insert data wrangling here
df_jobs[['date_posted', 'deadline']] = df_jobs.posted_deadline.str.split(' • Apply before ', expand = True)
df_jobs[['city', 'state']] = df_jobs.location.str.split(', ', expand = True)
df_jobs = df_jobs.drop(['location', 'posted_deadline'], axis=1)
df_jobs['deadline'] = pd.to_datetime(df_jobs['deadline'] + " 2023")

df_jobs.loc[df_jobs['city'].str.contains('Jakarta'), 'city'] = 'Jakarta'
df_jobs.loc[df_jobs['city'].str.contains('Bandung'), 'city'] = 'Bandung'
df_jobs.loc[df_jobs['city'].str.contains('Bogor'), 'city'] = 'Bogor'
df_jobs.loc[df_jobs['city'].str.contains('Malang'), 'city'] = 'Malang'
df_jobs.loc[df_jobs['city'].str.contains('Tangerang'), 'city'] = 'Tangerang'
df_jobs.loc[df_jobs['city'].str.contains('Sukabumi'), 'city'] = 'Sukabumi'
df_jobs.loc[df_jobs['city'].str.contains('Surabaya'), 'city'] = 'Surabaya'
df_jobs.loc[df_jobs['city'].str.contains('Semarang'), 'city'] = 'Semarang'
df_jobs.loc[df_jobs['city'].str.contains('Lombok'), 'city'] = 'Lombok'

city = df_jobs.groupby('city').count()

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{city["title"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = city.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)

if __name__ == "__main__": 
    app.run(debug=True)
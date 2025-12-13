import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

with open('insights_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

output_folder = "report_images_dark"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"Создана папка: {output_folder}")

plt.style.use('dark_background')

# настройка цветов
bg_color = '#121212'   # Очень темный серый фон
grid_color = '#333333' # Тусклая сетка
text_color = '#E0E0E0' # Светло-серый текст

plt.rcParams.update({
    'figure.facecolor': bg_color,
    'axes.facecolor': bg_color,
    'savefig.facecolor': bg_color,
    'text.color': text_color,
    'axes.labelcolor': text_color,
    'xtick.color': text_color,
    'ytick.color': text_color,
    'grid.color': grid_color,
    'grid.linestyle': '--',
    'axes.edgecolor': '#555555'
})

save_params = {'dpi': 300, 'bbox_inches': 'tight'}


def save_geo_chart(data):
    print("Генерация графика географии...")
    geo_data = pd.DataFrame(data['geographic_anomalies'])

    # Фильтрация: Удаляем ГОРЕЛОВО с типом НЕ ОПРЕДЕЛЕН
    mask = (geo_data['district'] == 'ГОРЕЛОВО') & (geo_data['disease_class'] == 'НЕ ОПРЕДЕЛЕН')
    geo_data_filtered = geo_data[~mask].copy()

    geo_data_sorted = geo_data_filtered.sort_values('excess_pct', ascending=False)

    plt.figure(figsize=(16, 10))

    chart = sns.barplot(
        data=geo_data_sorted,
        x='excess_pct',
        y='district',
        hue='disease_class',
        palette='bright',
        dodge=False
    )

    plt.title('Географические аномалии: Превышение заболеваемости над средней по городу', fontsize=18, pad=20)
    plt.xlabel('Процент превышения (Excess %)', fontsize=14)
    plt.ylabel('Район', fontsize=14)

    plt.legend(title='Класс заболеваний', bbox_to_anchor=(0.5, -0.15), loc='upper center', frameon=False)

    for i in chart.containers:
        chart.bar_label(i, fmt='%.1f%%', padding=3, color=text_color)

    filename = os.path.join(output_folder, '01_geo_anomalies_excess.png')
    plt.savefig(filename, **save_params)
    plt.close()
    print(f"Сохранено: {filename}")

def save_geo_low_excess_chart(data):
    print("Генерация графика малых аномалий (<10%)...")
    geo_data = pd.DataFrame(data['geographic_anomalies'])

    mask_exclude = (geo_data['district'] == 'ГОРЕЛОВО') & (geo_data['disease_class'] == 'НЕ ОПРЕДЕЛЕН')
    geo_data_clean = geo_data[~mask_exclude].copy()

    low_excess_data = geo_data_clean[geo_data_clean['excess_pct'] < 10].copy()

    if low_excess_data.empty:
        print("Нет аномалий с превышением менее 10%.")
        return

    low_excess_data = low_excess_data.sort_values('excess_pct', ascending=False)

    plt.figure(figsize=(16, 10))

    chart = sns.barplot(
        data=low_excess_data,
        x='excess_pct',
        y='district',
        hue='disease_class',
        palette='bright',
        dodge=False
    )

    plt.title('Малые географические аномалии (превышение < 10%)', fontsize=18, pad=20)
    plt.xlabel('Процент превышения (Excess %)', fontsize=14)
    plt.ylabel('Район', fontsize=14)

    plt.legend(title='Класс заболеваний', bbox_to_anchor=(0.5, -0.15), loc='upper center', frameon=False)

    for i in chart.containers:
        chart.bar_label(i, fmt='%.2f%%', padding=3, color=text_color, fontsize=10)

    filename = os.path.join(output_folder, '01_geo_anomalies_low_excess.png')
    plt.savefig(filename, **save_params)
    plt.close()
    print(f"Сохранено: {filename}")


def save_demographics_chart(data):
    print("Генерация демографического графика...")
    demo_list = []
    cat_map = {
        'elderly_diseases': 'Пожилые',
        'youth_diseases': 'Молодежь',
        'female_diseases': 'Женщины',
        'male_diseases': 'Мужчины'
    }

    for cat_key, cat_label in cat_map.items():
        for item in data['demographic_insights'].get(cat_key, []):
            item['Category'] = cat_label
            demo_list.append(item)

    df_demo = pd.DataFrame(demo_list)

    plt.figure(figsize=(14, 9))

    sns.scatterplot(
        data=df_demo,
        x='avg_age',
        y='female_pct',
        size='total_cases',
        hue='Category',
        sizes=(200, 3000),
        alpha=0.7,
        palette='bright',
        edgecolor='white', # Белая обводка пузырьков для контраста
        linewidth=1
    )

    for i in range(df_demo.shape[0]):
        plt.text(
            df_demo.avg_age[i],
            df_demo.female_pct[i],
            df_demo.code[i],
            fontsize=11,
            weight='bold',
            color='white',
            ha='center',
            va='center'
        )

    plt.title('Демография болезней', fontsize=18)
    plt.xlabel('Средний возраст (лет)', fontsize=12)
    plt.ylabel('Доля женщин (%)', fontsize=12)
    plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', title='Группа', frameon=False)
    plt.grid(True, linestyle='--', alpha=0.3)

    filename = os.path.join(output_folder, '02_demographics.png')
    plt.savefig(filename, **save_params)
    plt.close()
    print(f"Сохранено: {filename}")


def save_seasonality_heatmap(data):
    print("Генерация карты сезонности...")
    season_rows = []
    for code, details in data['disease_trends'].items():
        # Короткое имя для Y-оси
        name_short = f"{code}"
        for month_stat in details['stats']['seasonality']:
            season_rows.append({
                'Disease': name_short,
                'Month': month_stat['month'],
                'Cases': month_stat['avg_cases_per_week']
            })

    df_season = pd.DataFrame(season_rows)
    pivot_table = df_season.pivot(index='Disease', columns='Month', values='Cases')

    plt.figure(figsize=(16, 8))
    sns.heatmap(pivot_table, cmap="inferno", annot=True, fmt=".0f",
                linewidths=1, linecolor=bg_color,
                cbar_kws={'label': 'Ср. кол-во случаев'})

    plt.title('Сезонность заболеваний (Heatmap)', fontsize=18)
    plt.xlabel('Месяц', fontsize=14)
    plt.ylabel('Код МКБ-10', fontsize=14)

    filename = os.path.join(output_folder, '03_seasonality_heatmap.png')
    plt.savefig(filename, **save_params)
    plt.close()
    print(f"Сохранено: {filename}")


def save_all_trends(data):
    print("Генерация трендов...")
    trends_folder = os.path.join(output_folder, "trends")
    if not os.path.exists(trends_folder):
        os.makedirs(trends_folder)

    for disease_code, details in data['disease_trends'].items():
        trend_name = details['name']
        stats = details['stats']

        df_timeline = pd.DataFrame(stats['timeline'])
        df_timeline['date'] = pd.to_datetime(df_timeline['date'])

        plt.figure(figsize=(14, 7))

        plt.plot(df_timeline['date'], df_timeline['cases'],
                 label='Случаи', color='#555555', alpha=0.5, linewidth=1)

        plt.plot(df_timeline['date'], df_timeline['rolling_mean'],
                 label='Тренд (Mean)', color='#00FFFF', linewidth=2.5,  path_effects=[plt.matplotlib.patheffects.SimpleLineShadow(), plt.matplotlib.patheffects.Normal()])

        if 'peaks' in stats:
            peaks = pd.DataFrame(stats['peaks'])
            peaks['date'] = pd.to_datetime(peaks['date'])
            plt.scatter(peaks['date'], peaks['value'],
                        color='#FFD700', s=80, label='Пики', zorder=5, edgecolors='black')

        plt.title(f"{disease_code}: {trend_name}", fontsize=16, color='white')
        plt.xlabel('Дата')
        plt.ylabel('Случаи')

        legend = plt.legend(facecolor=bg_color, edgecolor=bg_color)
        for text in legend.get_texts():
            text.set_color("white")

        plt.grid(True, alpha=0.15)

        safe_filename = f"trend_{disease_code}.png"
        full_path = os.path.join(trends_folder, safe_filename)
        plt.savefig(full_path, **save_params)
        plt.close()
        print(f"   -> {disease_code}")


if __name__ == "__main__":
    import matplotlib.patheffects as path_effects

    save_geo_chart(data)
    save_geo_low_excess_chart(data)
    save_demographics_chart(data)
    save_seasonality_heatmap(data)
    save_all_trends(data)
    print(f"\nГотово! Результаты в папке: {output_folder}")
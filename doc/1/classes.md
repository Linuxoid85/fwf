# Список классов

## `_Settings`

Класс для получения параметров API

## `FWFLocatMgr`

Поиск нужной локации. Использование:

```python
locate = FWFLocatMgr(city_name: str)
```

`city_name` - название локации. Формат: `нас.пункт,область,страна`. Поля
`область` и `страна` необязательны, но они повышают точность выдачи поиска.

## `FForecast`

> **Внимание:** скоро этот класс будет переименован в `FWForecast`.

Получение основных сведений о погоде (дата, часовой пояс, описание текущей
погоды, дата восхода и захода Солнца, Луны, температура воздуха, влажность)

Использование:

```python
forecats = FForecast(coords: dict, _type: str)
```

`coords` - координаты локации, которые были получены методом `search_location()`
класса `FWFLocatMgr`. Формат:

```python
coords = {
    'lat': lat,
    'lon': lon
}
```

`_type` - тип:

- `current` - прогноз сейчас;
- `hourly` - почасовой прогноз (48 часов);
- `daily` - посуточный прогноз (8 суток);

### TODO:

- Добавление метода для получения сведений о давлении;
- Добавление метода для получения сведений о ветре, дожде и снеге;

## `FWFPlots`

Создание разных графиков.

Использование:

```python
plot = FWFPlots(coords: dict, _type: str)
```

`coords` - координаты локации, которые были получены методом `search_location()`
класса `FWFLocatMgr`. Формат:

```python
coords = {
    'lat': lat,
    'lon': lon
}
```

`_type` - тип:

- `current` - прогноз сейчас;
- `hourly` - почасовой прогноз (48 часов);
- `daily` - посуточный прогноз (8 суток);

### TODO:

На данный момент методы класса в состоянии создавать график изменения
температуры по часам и по дням. В планах добавить создание графиков и для других
изменяемых данных.

## `FWFAirPoll`

Получение информации о загрязнении воздуха (см. также информацию на
[OpenWeatherMap](https://openweathermap.org/)).

##### World of Tanks - Mods

## .. GUIFlash ..

Copyright: (c) 2017-2019 GambitER, since 2020 CH4MPi

This project is maintained by CH4MPi

## English
Allows you to dynamically create components for displaying text and graphic information in the Flash interface of the game World of Tanks. Components are created and managed using Python scripts (client modifications).

Learn more @ [**Wiki**](https://github.com/CH4MPi/GUIFlash/wiki).

## Russian
Позволяет динамически создавать компоненты для отображения текстовой и графической информации в Flash интерфейсе игры World of Tanks. Создание и управление компонентами производится через Python скрипты (модификации клиента)._

Подробнее в [**Wiki**](https://github.com/GambitER/GUIFlash/wiki).


![https://img.shields.io/badge/Status-WIP-orange](https://img.shields.io/badge/Status-WIP-orange) ![https://img.shields.io/badge/Realese-Yes-green](https://img.shields.io/badge/Realese-Yes-green) ![https://img.shields.io/badge/Python-2.7-blue](https://img.shields.io/badge/Python-2.7-blue)

## Changelog

### 0.6.7
* Compatibility with the World of Tanks EU client 2.4.1: the Scaleform view registry is no longer a module level
  `gui.Scaleform.framework.g_entitiesFactories` there. Added `gambiter/compat.py`, a single cross realm accessor
  (`getEntitiesFactories()`, `addSettings()`, `removeSettings()`), and switched `gambiter/flash.py` to it. On Lesta
  (RU) clients the module level registry is still used, so behaviour is unchanged; on EU the registry is reached
  through `dependency.instance(IGuiLoader).entitiesFactory`.
* No changes to the ActionScript sources: the SWF is identical to 0.6.6.
* Attribution unchanged: (c) 2017-2019 GambitER, since 2020 CH4MPi.

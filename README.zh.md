# **Python踩地雷工人**

[en](./README.md) &emsp;

一個小小的project

code**超級超級**凌亂

## **前置作業**

**注意!** 要在windows系統上才能使用

1. 下載[Minesweeper X](https://minesweepergame.com/download/minesweeper-x.php)、[Arbiter](https://minesweepergame.com/download/arbiter.php)或任何minesweeper的clone(推薦Arbiter)，並開啟
2. 在顯示設定中，將縮放調整到125%(之後會改良這個我保證)
3. 在終端機執行
```
$ git clone https://github.com/jasonjustin/python-minesweeper-solver.git
$ pip install -r requirements.txt
$ cd python-minesweeper-solver
```

# **使用方法**

## **概要**

```
$ python solver.py [-m <mode>] [-t <times>] [-h | --help]
```

## **簡介**

此程式會自動找到螢幕上開起的踩地雷程式，並將他解完

他可以從頭開始自己解，也可以接手你解到一半的遊戲

**注意: 若是要接手，最左上的方塊必須是未開啟的狀態**

並且有多次數模式，使用者可以指定要解幾盤遊戲，且結束會統計輸贏數據

## **參數們**

**`-h`  
`--help`**  
顯示參數們  

**`-m`  
`--mode`**  
遊戲模式，初階(beginner)為B，中階(intermediate)為I，高階(expert)為E。預設為高階模式。  

**`-t`  
`--times`**  
多次數模式，若不輸入則預設只解一次。

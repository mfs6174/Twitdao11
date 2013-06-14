##  关于twitdao11 

fork自 https://github.com/tongsu/twitdao/ 2013年6月12日twitter关闭了API 1,只能使用API1.1,我做了一些修改来适应这些变化

##  twitdao11与twitdao的不同之处
1. 修改API调用,除了list部分(太复杂我又不常用就不弄了)和一些api1.1不再支持的功能,大部分功能可以使用
2. 提高自动刷新的间隔,降低自动刷新频率,防止不断出现rate-limit问题(15分钟15次最多)
3. 添加了一些try except,修改一些小细节,在api出现兼容性问题/网络不好的情况下可以保持显示/重新fetch而不是报错.





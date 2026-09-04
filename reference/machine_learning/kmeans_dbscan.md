# K-Means 与 DBSCAN 聚类（K-Means and DBSCAN Clustering）

## 1. 适用问题

K-Means 适合尺度可比、近似凸且大小相近的簇；DBSCAN 适合以局部密度定义、形状不规则并希望标记噪声的簇。两者用于探索群体结构，不自动产生真实类别。

## 2. 不适用或需谨慎的情况

高维、混合类型、强尺度差异和密度变化大时，两者都可能不稳。K-Means 不适合非球状簇或大量异常点；DBSCAN 在不同密度并存、距离退化或参数缺乏依据时较困难。

## 3. 核心思想

K-Means 交替分配最近中心并更新均值，最小化簇内平方距离；DBSCAN 根据半径 $\varepsilon$ 内邻居数识别核心点，并将密度可达点连接成簇。先画图和做简单分层，再判断“簇”是否具有任务意义。两种算法回答的是不同的结构问题：前者强制每个样本归入某个中心，后者允许样本保持为噪声，因此簇数和噪声比例不能脱离参数比较。

## 4. 基本数学形式

K-Means 目标为

$$
\min_{C_1,\ldots,C_K}\sum_{k=1}^{K}\sum_{x_i\in C_k}\|x_i-\mu_k\|_2^2。
$$

DBSCAN 将邻域 $N_\varepsilon(x)=\{y:d(x,y)\le\varepsilon\}$ 中点数至少为 `min_samples` 的点视为核心点。

## 5. 输入、输出与主要假设

输入为特征、距离、缩放和超参数；输出为簇标签、中心或噪声标记。K-Means 假设均值和欧氏距离有意义；DBSCAN 假设同簇区域能用近似统一密度阈值连接。

## 6. 标准建模流程

选择有业务意义的特征；训练数据内缩放；用随机或规则分组作 Baseline；K-Means 比较多个 $K$ 和初始化，DBSCAN 结合邻域距离与领域尺度选择参数；解释每簇特征并检查小簇和噪声。

## 7. 评价与验证方式

结合轮廓系数、簇内离散度、Bootstrap/扰动稳定性和外部业务解释。更换缩放、特征、随机种子和参数后，用调整兰德指数等比较标签一致性；检查每簇样本量及画像的置信区间。若用于下游策略，应在独立数据上验证策略收益，并确认新样本的归类规则可执行。

## 8. 优点

K-Means 快速且中心易概括；DBSCAN 不需预设簇数，可发现非凸簇并显式标记低密度点。

## 9. 局限

K-Means 易受初值与异常点影响；DBSCAN 对 $\varepsilon$、`min_samples` 和维度敏感。内部指标偏好特定几何，不能替代领域有效性。DBSCAN 本身没有像质心那样直接的新样本预测规则；若比赛任务需要持续分群，必须另行定义部署流程。

## 10. 华为杯常见用法

用于城市、客户、设备或工况分群。论文应说明特征和距离为何合理，展示参数敏感性与簇画像，并避免把聚类编号直接当作优劣等级。

## 11. 常见误用

只凭肘部图确定唯一 $K$；未缩放就用欧氏距离；把噪声点全部删除；用同一 DBSCAN 参数处理密度差异巨大的区域；以二维降维图的视觉分离证明高维聚类有效。

## 12. Python 实现建议

使用 scikit-learn `KMeans`、`DBSCAN`、`silhouette_score`。明确 `random_state` 和 `n_init`；大样本关注 DBSCAN 邻域计算的内存，必要时稀疏邻接或抽样诊断。

## 13. 权威参考

1. Ester, M., Kriegel, H.-P., Sander, J., Xu, X. A Density-Based Algorithm for Discovering Clusters in Large Spatial Databases with Noise. *KDD*, 1996：https://file.biolab.si/papers/1996-DBSCAN-KDD.pdf。
2. scikit-learn Documentation, Clustering：https://scikit-learn.org/stable/modules/clustering.html，访问日期：2026-09-04。

# Git 笔记：分支、HEAD 与 switch

## 一、三个核心概念

| 概念 | 是什么 | 比喻 |
|---|---|---|
| **提交（commit）** | 某个时刻项目的完整快照，创建后不会改变，用哈希值标识（如 `1461672`） | 相册里的一张照片 |
| **分支（branch）** | 一个**指向某个提交的标签**，有新提交时会自动往前移动 | 夹在相册里的书签 |
| **HEAD** | 表示"**我现在在这里**"，通常指向某个分支 | 你的手指，指着你正在看的书签 |

> 提交是照片，分支是书签，HEAD 是"我现在在哪"。

所有提交、分支、HEAD 都保存在项目根目录的 `.git` 文件夹里。一个 `.git` 对应一个仓库，管理所在文件夹及其所有子文件夹。

---

## 二、HEAD 的两种状态

### 1. 正常状态：HEAD 指向分支

```
init  ←  修改1
           ↑
          main
           ↑
          HEAD
```

- `git status` 第一行显示：`On branch main`
- `git log` 中显示：`(HEAD -> main)`
- 每次提交，`main` 往前移动，HEAD 跟着一起移动：

```
init  ←  修改1  ←  修改2
                     ↑
                    main ← HEAD
```

**日常开发中，HEAD 几乎总是跟着某个分支。**

### 2. 游离状态（detached HEAD）：HEAD 直接指向某个提交

```
init  ←  修改1
 ↑         ↑
HEAD      main
```

- `git status` 第一行显示：`HEAD detached at 1461672`
- 工作区的文件变成了该提交时的样子
- `main` 不受影响，仍然指向 `修改1`

**判断依据**：是否游离取决于切换时用的是**分支名还是提交哈希**，和版本新旧无关。

| 命令 | 结果 |
|---|---|
| `git switch main` | 正常状态，HEAD 跟着 `main` |
| `git switch --detach e0cd902` | 游离状态，即使 `main` 也正好指向 `e0cd902` |
| `git switch --detach HEAD` | 游离状态，虽然位置没变，但脱离了分支 |

**游离状态常见场景**（一般都是临时的）：

- 主动查看旧版本或标签：`git switch --detach 哈希`
- `rebase` 进行到一半、`git bisect` 二分查找 bug（Git 自动进入）
- CI/CD、子模块检出代码

> **原则：写代码、提交代码，都要在分支上进行。** 不要在游离状态下提交。

---

## 三、git switch 常用操作

```powershell
git switch main                      # 切换到 main 分支
git switch -c 新分支名               # 在当前位置新建分支并切换过去
git switch -c 新分支名 哈希          # 在某个历史版本上新建分支并切换过去
git switch --detach 哈希             # 查看某个历史版本（进入游离状态）
git switch -                         # 切回上一个所在的分支
```

### switch 与 checkout 的区别

```powershell
git checkout e0cd902          # 老命令：直接进入游离状态，只给一个警告，容易误操作
git switch e0cd902            # 报错，要求明确加 --detach
git switch --detach e0cd902   # 明确表示要进入游离状态
```

推荐使用 `switch`，因为它要求你明确表态。

---

## 四、切换时工作区会发生什么

**Git 管理的文件会全部变成目标版本的内容。**

- 文件内容变成目标版本的样子
- 目标版本里没有的文件会从磁盘上暂时消失，切回来后会重新出现

**不会被改动的文件：**

| 文件类型 | 切换时 |
|---|---|
| 未跟踪的文件（从没 `add` 过） | 原样保留 |
| 被 `.gitignore` 忽略的文件（`__pycache__/`、`.venv/`、`.env`） | 原样保留 |
| 未提交的修改 | 见下面 |

**未提交的修改：**

- **和目标版本不冲突**：修改会被带到新的位置
- **会被目标版本覆盖**：Git **拒绝切换**，报错：
  ```
  error: Your local changes to the following files would be overwritten by checkout
  ```

处理方法：

```powershell
git commit -am "临时提交"   # 方法一：先提交
git stash                   # 方法二：临时存起来，切回来后用 git stash pop 恢复
git restore 文件名          # 方法三：确定不要了，直接丢弃
```

---

## 五、为什么切到旧版本后，新的提交"消失"了

`git log` 和编辑器的提交图，默认都是**从 HEAD 开始往回找**。每个提交只记得它的上一个提交，所以 HEAD 在 `init` 时，看不到它后面的 `修改1`。

**提交并没有消失，它还在 `main` 分支上。**

```powershell
git log --oneline --all     # 查看所有分支的提交
git switch main             # 回到 main，就能重新看到
```

---

## 六、在历史版本上创建分支

```powershell
git switch -c old-version 1461672    # 创建并切换（最常用）
git branch old-version 1461672       # 只创建，不切换
git switch -c old-version            # 已在游离状态时，在当前位置建分支
git switch -c hotfix v1.0            # 基于标签创建分支
```

创建后再提交，历史会**分叉**：

```
              修改1      ← main
            ↗
init
            ↘
              旧版修复   ← old-version ← HEAD
```

两条分支互相独立。以后可以用 `git merge` 把修复合并回 `main`。

推送新分支到远程：

```powershell
git push -u github old-version
```

**典型场景**：线上运行 `v1.0`，`main` 上有还没准备好发布的新功能。线上出 bug 时，用 `git switch -c hotfix v1.0` 修复并单独发布，再合并回 `main`。

---

## 七、恢复与找回版本

### 恢复某个文件：git restore

```powershell
git restore --source=哈希 main.py            # main.py 恢复到指定版本
git restore --source=HEAD~1 main.py          # 恢复到上一次提交的版本
git restore main.py                          # 不写 --source：从暂存区恢复，丢弃未 add 的修改
git restore --staged main.py                 # 撤销 add，修改保留在工作区
```

只改文件内容，不动提交历史。恢复后要保存结果，需要再 `add` 和 `commit`。

`--source` 可以写：哈希值、`HEAD`、`HEAD~1`、`HEAD~2`、分支名（`main`、`github/main`）、标签（`v1.0`）。

### 整个分支回退：git reset（只用于还没推送的提交）

| 命令 | 提交历史 | 被撤掉的修改 |
|---|---|---|
| `git reset --soft 哈希` | 回退 | 保留在暂存区 |
| `git reset 哈希` | 回退 | 保留在工作区 |
| `git reset --hard 哈希` | 回退 | **直接丢弃** |

### 撤销已推送的提交：git revert

```powershell
git revert 哈希      # 新增一个"反向提交"来抵消修改，不改写历史
git push
```

### 后悔药：git reflog

```powershell
git reflog                     # 查看 HEAD 的所有移动记录
git reset --hard HEAD@{1}      # 回到上一步的状态
```

---

## 八、提交过的版本能找回吗

**只要提交过，并且 `.git` 文件夹还在，基本都能找回。**

| 情况 | 用什么找 |
|---|---|
| 提交还在某个分支上 | `git log --oneline --all` |
| 提交不在任何分支上（`reset --hard` 掉了、游离状态下提交后切走了） | `git reflog` |

**会真的丢失的情况：**

1. 从来没提交过的修改
2. 删除了 `.git` 文件夹或整个项目（没推送到远程）
3. 不在任何分支上、且超过约 30 天的提交（会被 Git 自动清理）
4. 换电脑重新 clone（`reflog` 只存在于本机）
5. `git push --force` 覆盖了远程历史

**好习惯：**

- 勤提交，勤推送
- 重要版本打标签：`git tag v1.0`
- 不在游离状态下提交，要改旧版本先建分支
- 执行 `reset --hard` 前先 `git status`

---

## 九、速查表

| 我想…… | 命令 |
|---|---|
| 知道自己现在在哪 | `git status`（看第一行） |
| 看所有分支的提交 | `git log --oneline --all` |
| 看看某个旧版本 | `git switch --detach 哈希` |
| 看完回来 | `git switch main` |
| 在旧版本上新建分支 | `git switch -c 分支名 哈希` |
| 游离状态下想保留修改 | `git switch -c 分支名` |
| 恢复单个文件到旧版本 | `git restore --source=哈希 文件名` |
| 回退还没推送的提交 | `git reset 哈希` |
| 撤销已推送的提交 | `git revert 哈希` |
| 找回"丢失"的提交 | `git reflog` |

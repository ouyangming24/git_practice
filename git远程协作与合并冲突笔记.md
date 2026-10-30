# Git 笔记：push、pull、合并与冲突

> 本笔记中远程仓库名为 `github`（用 `git clone` 得到的仓库默认叫 `origin`），主分支为 `main`。

## 一、远程仓库基础

| 概念 | 说明 |
|---|---|
| **远程仓库（remote）** | 云端的仓库，比如 GitHub 上的仓库。本地用一个别名代表它，比如 `github` 或 `origin` |
| **远程分支（如 `github/main`）** | 本地记录的"上次同步时云端 `main` 在哪"。只有 `fetch`、`pull`、`push` 时才会更新 |
| **跟踪关系（upstream）** | 本地 `main` 和 `github/main` 绑定后，直接写 `git push`、`git pull` 就行 |

```powershell
git remote -v                                   # 查看远程仓库地址
git remote add github git@github.com:用户/仓库.git   # 添加远程仓库
git remote set-url github 新地址                 # 修改远程仓库地址
git branch -vv                                  # 查看本地分支和远程分支的跟踪关系
```

### 跟踪关系（绑定）

在某个分支上直接运行 `git push` 或 `git pull`（不写远程名和分支名）时，Git 会使用 `git branch -vv` 里方括号显示的远程分支：

```
* main         a1b2c3d [github/main: ahead 2] 修改2
  old-version  1461672 init
```

- `main` 绑定了 `github/main`：直接 `git push` 会推送到 `github/main`，`git pull` 也从这里拉取
- `old-version` 没有方括号，说明还没绑定：直接 `git push` 会报错 `has no upstream branch`
- `ahead 2` 表示本地比远程多 2 个提交（需要推送），`behind 1` 表示远程比本地多 1 个提交（需要拉取）。这个数字基于上次 `fetch` 的信息，想看最新情况要先 `git fetch`

**修改绑定：**

```powershell
git branch -u github/main                # 把当前分支绑定到 github/main
git branch -u github/main old-version    # 给指定分支修改绑定（不用切换过去）
git branch --unset-upstream              # 解除当前分支的绑定
git push -u github 分支名                # 推送的同时建立或修改绑定，远程分支不存在时会自动创建
```

改完后用 `git branch -vv` 确认。

> [!IMPORTANT]
> **注意 1：`git push` 只推送当前所在的分支**，不会把所有分支一起推上去。
>
> **注意 2：`git branch -u` 要求远程分支已经存在。** 报错 `the requested upstream branch 'github/xxx' does not exist` 时：
> - 云端有这个分支，只是本地还不知道：先 `git fetch`，再绑定
> - 云端还没有这个分支：用 `git push -u github 分支名`，推送的同时完成创建和绑定
>
> **注意 3：本地分支和远程分支尽量同名。** Git 默认要求两边同名才能直接 `git push`。如果本地 `dev` 绑定了 `github/main`，`git pull` 能用，但 `git push` 会被拒绝，必须写明目标：
> ```powershell
> git push github dev:main    # 把本地 dev 推送到远程的 main
> ```

> [!TIP]
> 设置 `git config --global push.autoSetupRemote true` 后，新分支第一次直接 `git push` 就会自动创建同名远程分支并完成绑定，不用再写 `-u github 分支名`。

---

## 二、push：把本地提交推送到云端

```powershell
git push -u github main        # 第一次推送，同时建立跟踪关系
git push                       # 建立跟踪关系后，直接推送
git push -u github feature     # 推送新分支，云端会自动创建同名分支
git push github --delete feature   # 删除云端分支
```

**push 只推送已提交的内容**，未提交的修改不会被推送。

### push 被拒绝

```
! [rejected]  main -> main (fetch first)
```

原因：云端有你本地没有的提交（比如别人推送过，或者你在网页上改过）。

解决：先拉取合并，再推送：

```powershell
git pull
git push
```

### 强制推送（谨慎使用）

```powershell
git push --force-with-lease
```

- 会用本地历史**覆盖**云端历史，一般在 `reset`、`rebase` 改写已推送的提交后使用
- `--force-with-lease` 比 `--force` 安全：如果云端有你没见过的新提交，它会拒绝推送
- **只在自己一个人用的分支上使用**，团队共享的分支（如 `main`）不要强制推送

---

## 三、fetch 与 pull：从云端拉取

| 命令 | 做了什么 | 会改动工作区的文件吗 |
|---|---|---|
| `git fetch` | 只下载云端的新提交，更新 `github/main` | **不会** |
| `git pull` | `fetch` + `merge`：下载后合并到当前分支 | **会**，以合并的方式更新，不是直接覆盖 |

### 先看再合并（稳妥做法）

```powershell
git fetch
git log --oneline main..github/main    # 云端比本地多了哪些提交
git log --oneline github/main..main    # 本地比云端多了哪些提交（还没推送的）
git diff main github/main              # 两边内容的具体差异
git pull                               # 确认没问题后再合并
```

### pull 时的几种情况

| 情况 | 结果 |
|---|---|
| 本地没有新提交，工作区干净 | 快进合并，本地直接更新到云端版本 |
| 本地和云端都有新提交，改的地方不同 | 自动合并，两边的修改都保留，生成一个合并提交 |
| 本地和云端改了同一文件的同一位置 | **发生冲突**，需要手动解决 |
| 本地有未提交的修改，且与云端改动的文件重叠 | **拒绝拉取**：`Your local changes ... would be overwritten by merge` |
| 本地有未提交的修改，但与云端改动的文件不重叠 | 正常拉取，你的修改保留 |
| 未跟踪文件、被忽略的文件 | 不受影响（除非云端新增了同名文件，此时会拒绝拉取） |

### 新版 Git 首次 pull 可能报错

```
fatal: Need to specify how to reconcile divergent branches.
```

设置一次默认合并方式即可：

```powershell
git config --global pull.rebase false    # 用 merge 方式（默认，推荐新手使用）
git config --global pull.rebase true     # 用 rebase 方式（历史更整洁，见第六节）
```

### 拉取一个本地还没有的远程分支

```powershell
git fetch
git switch feature      # 自动创建本地 feature 分支，并跟踪 github/feature
```

---

## 四、merge：合并分支

```powershell
git switch main         # 1. 先切换到"接收修改"的分支
git merge feature       # 2. 把 feature 合并进来
```

**口诀：站在哪个分支上，就是把别的分支合并进来。**

### 1. 快进合并（fast-forward）

`main` 在分出 `feature` 后没有新提交：

```
合并前：
init ← A               ← main
         ↖
           B ← C       ← feature

合并后：main 直接前移，不产生新提交
init ← A ← B ← C       ← main, feature
```

### 2. 三方合并（产生合并提交）

两个分支各自都有新提交：

```
合并前：
init ← A ← D           ← main
         ↖
           B ← C       ← feature

合并后：生成一个新的合并提交 M，它有两个父提交
init ← A ← D ←── M     ← main
         ↖      ↙
           B ← C       ← feature
```

执行时 Git 可能会打开编辑器让你确认合并提交的信息，保存并关闭即可。

### 常用选项

```powershell
git merge feature --no-ff     # 即使能快进，也强制生成合并提交，保留"曾经有个分支"的痕迹
git merge --abort             # 合并出问题时，放弃这次合并，回到合并前的状态
git branch -d feature         # 合并完成后删除本地分支
git branch --merged           # 查看哪些分支已经合并到当前分支
```

---

## 五、冲突：两边改了同一处

### 冲突长什么样

合并或拉取时出现：

```
CONFLICT (content): Merge conflict in calculator.py
Automatic merge failed; fix conflicts and then commit the result.
```

打开冲突文件，会看到 Git 插入的标记：

```python
<<<<<<< HEAD
def add(a, b):
    return a + b          # 当前分支（你本地）的版本
=======
def add(a, b):
    return round(a + b, 2)   # 被合并进来的版本
>>>>>>> feature
```

| 标记 | 含义 |
|---|---|
| `<<<<<<< HEAD` 到 `=======` | 当前分支的内容 |
| `=======` 到 `>>>>>>> feature` | 被合并进来的分支的内容 |

### 解决冲突的步骤

```powershell
git status                 # 1. 查看哪些文件有冲突（显示为 both modified）
                           # 2. 打开文件，手动修改成最终想要的样子，删除所有 <<<<<<< ======= >>>>>>> 标记
git add calculator.py      # 3. 标记这个文件的冲突已解决
git commit                 # 4. 完成合并（会自动生成合并提交信息）
```

**最终内容由你决定**：可以保留一边、保留两边，也可以重新写。

### 在 Cursor 里解决冲突

冲突文件上方会出现几个快捷按钮：

| 按钮 | 作用 |
|---|---|
| Accept Current Change | 保留当前分支的版本 |
| Accept Incoming Change | 保留合并进来的版本 |
| Accept Both Changes | 两边都保留 |
| Compare Changes | 并排对比两边的差异 |

处理完后保存文件，在源代码管理面板中暂存（相当于 `git add`），再提交即可。

### 不想处理了，放弃这次合并

```powershell
git merge --abort      # 合并时冲突
git rebase --abort     # rebase 时冲突
```

都会回到操作前的状态。

### 减少冲突的习惯

- 开始工作前先 `git pull`，保持和云端同步
- 勤提交、勤推送，不要攒一大堆修改
- 一个分支只做一件事，尽早合并
- 团队中避免多人同时修改同一个文件的同一块区域

---

## 六、pull 的另一种方式：rebase

```powershell
git pull --rebase
```

和普通 `pull` 的区别：不生成合并提交，而是把你本地的新提交"挪"到云端最新提交的后面，历史是一条直线。

```
普通 pull（merge）：                pull --rebase：
A ← B ← M   ← main                  A ← C ← B'   ← main
  ↖   ↙                             （B 被重新放到 C 后面）
    C
```

rebase 时遇到冲突的处理方法：

```powershell
# 修改冲突文件后
git add 文件名
git rebase --continue      # 继续
git rebase --abort         # 或者放弃，回到 rebase 前的状态
```

> **注意**：rebase 会改写提交历史，**不要对已经推送、且别人在用的提交进行 rebase**。

---

## 七、stash：拉取或切换前临时存放修改

工作做到一半，需要先 `pull` 或切换分支，但又不想提交：

```powershell
git stash              # 把未提交的修改临时存起来，工作区变干净
git pull               # 做别的事
git stash pop          # 把存起来的修改恢复回来

git stash list         # 查看存了哪些
git stash -u           # 连未跟踪的新文件一起存
```

`stash pop` 时也可能发生冲突，解决方法和合并冲突相同。

---

## 八、日常协作流程

```powershell
# 开始工作前
git switch main
git pull

# 新建分支开发
git switch -c feature-xxx
# ……修改代码……
git add .
git commit -m "完成 xxx 功能"
git push -u github feature-xxx

# 开发完成，合并回 main
git switch main
git pull                    # 先同步云端最新的 main
git merge feature-xxx       # 合并（有冲突就解决）
git push

# 清理分支
git branch -d feature-xxx
git push github --delete feature-xxx
```

> 团队中通常不在本地直接合并 `main`，而是推送分支后在 GitHub 上发起 **Pull Request（PR）**，经过代码审查后在网页上合并。

---

## 九、常见报错速查

| 报错 | 原因 | 解决 |
|---|---|---|
| `rejected ... (fetch first)` | 云端有本地没有的提交 | `git pull` 后再 `git push` |
| `rejected ... (non-fast-forward)` | 本地历史和云端分叉了 | `git pull` 合并；确实要覆盖时用 `--force-with-lease` |
| `has no upstream branch` | 还没建立跟踪关系 | `git push -u github 分支名` |
| `Need to specify how to reconcile divergent branches` | 没设置 pull 的合并方式 | `git config --global pull.rebase false` |
| `Your local changes ... would be overwritten by merge` | 未提交的修改和云端改动冲突 | 先 `commit` 或 `stash` |
| `untracked working tree files would be overwritten` | 云端新增的文件和本地未跟踪文件同名 | 改名或删除本地文件后再拉取 |
| `CONFLICT (content): Merge conflict in xxx` | 两边改了同一处 | 手动解决后 `add` + `commit` |
| `Permission denied (publickey)` | SSH 密钥没有添加到 GitHub | 把公钥添加到 GitHub，或改用 HTTPS 地址 |
| `refusing to merge unrelated histories` | 两个仓库没有共同历史（比如云端建仓时勾选了 README） | `git pull github main --allow-unrelated-histories` |

---

## 十、命令速查表

| 我想…… | 命令 |
|---|---|
| 推送当前分支 | `git push` |
| 第一次推送某个分支 | `git push -u github 分支名` |
| 查看分支绑定关系 | `git branch -vv` |
| 修改当前分支的绑定 | `git branch -u github/分支名` |
| 只下载不合并 | `git fetch` |
| 下载并合并 | `git pull` |
| 拉取时不产生合并提交 | `git pull --rebase` |
| 看云端多了哪些提交 | `git log --oneline main..github/main` |
| 看还有哪些没推送 | `git log --oneline github/main..main` |
| 把某分支合并到当前分支 | `git merge 分支名` |
| 放弃正在进行的合并 | `git merge --abort` |
| 冲突解决后完成合并 | `git add 文件` → `git commit` |
| 临时存放修改 | `git stash` / `git stash pop` |
| 删除已合并的本地分支 | `git branch -d 分支名` |
| 删除云端分支 | `git push github --delete 分支名` |

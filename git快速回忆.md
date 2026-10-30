# Git 快速回忆

> 远程仓库名以 `github` 为例（`clone` 得到的默认叫 `origin`），主分支为 `main`。

---

## 0. 核心概念（一句话版）

| 概念 | 一句话 |
|---|---|
| 工作区 | 你在编辑器里看到、正在改的文件 |
| 暂存区 | `git add` 之后、`commit` 之前的"待提交清单" |
| 提交（commit） | 项目的一张完整快照，用哈希值标识，不会改变 |
| 分支（branch） | 指向某个提交的书签，提交时自动前移 |
| HEAD | "我现在在哪"，通常指向某个分支 |
| 游离 HEAD | HEAD 直接指向某个提交而不是分支，只适合临时查看 |
| 远程分支（`github/main`） | 本地记录的"上次同步时云端 main 在哪" |
| 跟踪关系（upstream） | 本地分支绑定的远程分支，`push`/`pull` 不写参数时用它 |
| `.git` 文件夹 | 整个仓库的历史都在这里，删了就没了 |

```
工作区  --add-->  暂存区  --commit-->  本地仓库  --push-->  远程仓库
工作区  <--------------- pull（= fetch + merge） ---------  远程仓库
```

---

## 1. 首次配置（每台电脑做一次）

```powershell
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
git config --global init.defaultBranch main      # 新仓库默认分支叫 main
git config --global core.quotepath false         # 中文文件名正常显示
git config --global pull.rebase false            # pull 默认用 merge
git config --global push.autoSetupRemote true    # 新分支首次 push 自动绑定（可选）
git config --global --list                       # 查看所有配置
```

### SSH 密钥（推送到 GitHub 用）

```powershell
ssh-keygen -t ed25519 -C "你的邮箱"                # 生成，一路回车
Get-Content ~\.ssh\id_ed25519.pub | Set-Clipboard  # 复制公钥
# GitHub → Settings → SSH and GPG keys → New SSH key → 粘贴
ssh -T git@github.com                              # 测试，看到 Hi xxx! 即成功
```

> 同一把公钥可以同时加到 GitHub 和 Gitee。

---

## 2. 创建仓库

```powershell
git init                          # 把当前文件夹变成仓库
git clone 地址                    # 克隆云端仓库（自动创建 origin 并绑定）
git clone 地址 文件夹名           # 克隆到指定文件夹
```

> 不要在用户目录或磁盘根目录 `git init`。

---

## 3. 日常提交

```powershell
git status                        # 看状态（最常用！）
git add 文件名                    # 加入暂存区
git add .                         # 加入当前目录下所有修改
git commit -m "提交信息"          # 提交
git commit -am "提交信息"         # 已跟踪文件：add + commit 一步完成（新文件不行）
```

> `git commit` 不带 `-m` 会打开编辑器：第 1 行写信息 → 保存 → 关闭标签页。空信息会取消提交。

### .gitignore

```gitignore
__pycache__/        # 忽略文件夹
*.log               # 忽略某类文件
.env                # 忽略敏感配置
.venv/
```

```powershell
git rm --cached 文件名     # 文件已被跟踪，想让 .gitignore 生效：先从仓库移除（本地文件保留）
```

---

## 4. 查看历史与差异

```powershell
git log                           # 完整历史（按 q 退出）
git log --oneline                 # 一行一个提交
git log --oneline --all --graph   # 所有分支 + 分叉图
git show 哈希                     # 看某次提交改了什么

git diff                          # 工作区 vs 暂存区（还没 add 的修改）
git diff --staged                 # 暂存区 vs 最新提交（add 了还没 commit 的）
git diff 哈希1 哈希2              # 两个版本之间的差异
git diff main github/main         # 本地和云端的差异
```

**版本的写法**：哈希（`1461672`）、`HEAD`、`HEAD~1`（上一个）、`HEAD~2`、分支名、`github/main`、标签名

---

## 5. 撤销与回退

| 我想…… | 命令 |
|---|---|
| 丢弃工作区的修改（还没 add） | `git restore 文件名` |
| 撤销 add（修改保留在工作区） | `git restore --staged 文件名` |
| 把某个文件恢复到指定版本 | `git restore --source=哈希 文件名` |
| 修改最后一次提交的信息或补漏文件 | `git add 漏的文件` → `git commit --amend` |
| 回退提交，修改留在暂存区 | `git reset --soft 哈希` |
| 回退提交，修改留在工作区 | `git reset 哈希` |
| 回退提交，修改**全部丢弃** | `git reset --hard 哈希` |
| 撤销**已推送**的提交 | `git revert 哈希` → `git push` |
| 找回"丢失"的提交 | `git reflog` → `git reset --hard 哈希` |

**规则：**

- 没推送 → 用 `reset` / `--amend`
- 已推送 → 用 `revert`（新增反向提交，不改写历史）
- `reset --hard` 前先 `git status`，未提交的修改会真的丢失
- 只要提交过且 `.git` 还在，基本都能用 `reflog` 找回

---

## 6. 分支与 HEAD

```powershell
git branch                        # 查看本地分支（* 是当前分支）
git branch -a                     # 包括远程分支
git branch -vv                    # 查看跟踪关系和 ahead/behind
git switch 分支名                 # 切换分支
git switch -c 新分支              # 在当前位置新建并切换
git switch -c 新分支 哈希         # 在历史版本上新建并切换
git switch -                      # 切回上一个分支
git switch --detach 哈希          # 查看旧版本（进入游离状态）
git branch -m 新名字              # 重命名当前分支（如 master → main）
git branch -d 分支名              # 删除已合并的分支
git branch -D 分支名              # 强制删除（未合并也删）
```

**切换时：**

- Git 管理的文件全部变成目标版本；未跟踪和被忽略的文件不变
- 未提交的修改：不冲突就带过去，会被覆盖就**拒绝切换** → 先 `commit` 或 `stash`
- 用分支名切 → 正常状态；用哈希切 → 游离状态
- 游离状态想保留修改：`git switch -c 新分支`；不小心切过来：`git switch main`
- 切到旧版本后"新提交消失"：没消失，用 `git log --oneline --all` 查看

**判断自己在哪**：`git status` 第一行

- `On branch main` → 正常
- `HEAD detached at xxx` → 游离

---

## 7. 远程仓库

```powershell
git remote -v                             # 查看远程地址
git remote add github 地址                # 添加远程
git remote set-url github 新地址          # 修改地址（如 HTTPS ↔ SSH）
git remote rename github origin           # 重命名
git remote remove github                  # 删除
```

**地址格式：**

- SSH：`git@github.com:用户/仓库.git`（需要配置密钥）
- HTTPS：`https://github.com/用户/仓库.git`（浏览器登录授权）

---

## 8. push 推送

```powershell
git push -u github main             # 首次推送 + 建立绑定
git push                            # 之后直接推（推送到 branch -vv 里的绑定）
git push -u github 新分支           # 推送新分支，云端自动创建同名分支
git push -u github main:新分支名    # 本地 main 推送到云端另一个名字的分支
git push github --delete 分支名     # 删除云端分支
git push --tags                     # 推送所有标签
git push --force-with-lease         # 强制推送（只在自己的分支上用）
```

- 只推送**当前分支**的**已提交**内容
- 默认要求本地和远程分支**同名**
- 云端没有该分支时，push 会**自动创建**，不需要先在网页上建

### 跟踪关系（绑定）

```powershell
git branch -vv                          # 查看：[github/main: ahead 2, behind 1]
git branch -u github/main               # 当前分支绑定到 github/main
git branch -u github/main 分支名        # 给指定分支绑定
git branch --unset-upstream             # 解除绑定
```

- `ahead 2`：本地多 2 个提交，需要 push
- `behind 1`：云端多 1 个提交，需要 pull
- 数字基于上次 `fetch`，想看最新先 `git fetch`

---

## 9. fetch / pull 拉取

| 命令 | 效果 | 改动工作区？ |
|---|---|---|
| `git fetch` | 只下载，更新 `github/main` | 不会 |
| `git pull` | fetch + merge | 会（合并，不是覆盖） |
| `git pull --rebase` | fetch + rebase，历史成一条直线 | 会 |

```powershell
git fetch
git log --oneline main..github/main     # 云端多了哪些提交
git log --oneline github/main..main     # 本地还有哪些没推送
git pull

git fetch → git switch 远程分支名        # 拉取本地还没有的远程分支
```

**pull 的保护机制：**

- 未提交的修改与云端改动重叠 → 拒绝拉取 → 先 `commit` 或 `stash`
- 未跟踪 / 被忽略的文件不受影响
- 两边改了同一处 → 冲突，手动解决

---

## 10. merge 合并

```powershell
git switch main          # 站在接收修改的分支上
git merge feature        # 把 feature 合并进来
git merge --no-ff feature  # 强制生成合并提交
git merge --abort        # 放弃合并
```

- **快进合并**：main 没有新提交 → main 直接前移
- **三方合并**：两边都有新提交 → 生成合并提交

---

## 11. 冲突

```python
<<<<<<< HEAD
当前分支的内容
=======
被合并进来的内容
>>>>>>> feature
```

**解决流程：**

```powershell
git status                 # 1. 找冲突文件（both modified）
                           # 2. 编辑成最终内容，删掉所有 <<<<<<< ======= >>>>>>> 标记
git add 文件名             # 3. 标记已解决
git commit                 # 4. 完成合并
```

- Cursor 中可点：Accept Current / Accept Incoming / Accept Both / Compare
- 不想处理了：`git merge --abort` 或 `git rebase --abort`
- 减少冲突：开工先 pull、勤提交勤推送、一个分支只做一件事

---

## 12. stash 临时存放

```powershell
git stash              # 把未提交的修改存起来，工作区变干净
git stash -u           # 连未跟踪的新文件一起存
git stash list         # 查看
git stash pop          # 恢复并删除这条记录
git stash apply        # 恢复但保留记录
git stash drop         # 删除最近一条
```

**场景**：活干一半，要切分支或 pull。

---

## 13. 标签 tag

```powershell
git tag v1.0                       # 给当前提交打标签
git tag v1.0 哈希                  # 给指定提交打标签
git tag -a v1.0 -m "说明"          # 带说明的标签
git tag                            # 查看所有标签
git push github v1.0               # 推送单个标签
git push --tags                    # 推送所有标签
git tag -d v1.0                    # 删除本地标签
git switch --detach v1.0           # 查看某个版本
git switch -c hotfix v1.0          # 基于版本建分支修 bug
```

---

## 14. rebase 与 cherry-pick

```powershell
git rebase main                    # 把当前分支的提交挪到 main 最新提交之后
git rebase -i HEAD~3               # 交互式整理最近 3 个提交（合并、改信息、删除）
git rebase --continue              # 解决冲突并 add 后继续
git rebase --abort                 # 放弃

git cherry-pick 哈希               # 把某个提交复制到当前分支
```

> rebase 会改写历史：**不要 rebase 已推送且别人在用的提交**。

---

## 15. 标准工作流程

```powershell
git switch main ; git pull                  # 1. 同步最新代码
git switch -c feature-xxx                   # 2. 新建功能分支
# …… 写代码 ……
git add . ; git commit -m "完成 xxx"         # 3. 提交
git push -u github feature-xxx              # 4. 推送分支
# 5. 在 GitHub 上发起 Pull Request，审查后合并
# 或者本地合并：
git switch main ; git pull ; git merge feature-xxx ; git push
git branch -d feature-xxx                   # 6. 清理分支
git push github --delete feature-xxx
```

---

## 16. 常见报错

| 报错 | 解决 |
|---|---|
| `not a git repository` | 不在仓库目录里，或还没 `git init` |
| `src refspec main does not match any` | 还没提交过，或分支名不叫 main |
| `has no upstream branch` | `git push -u github 分支名` |
| `Permission denied (publickey)` | 公钥没加到 GitHub，或改用 HTTPS |
| `remote origin already exists` | `git remote -v` 查看，用 `set-url` 修改 |
| `rejected ... (fetch first)` | 云端有新提交：先 `git pull` 再 `git push` |
| `rejected ... (non-fast-forward)` | 历史分叉：`git pull` 合并 |
| `refusing to merge unrelated histories` | `git pull github main --allow-unrelated-histories` |
| `Need to specify how to reconcile divergent branches` | `git config --global pull.rebase false` |
| `Your local changes ... would be overwritten` | 先 `commit` 或 `stash` |
| `untracked working tree files would be overwritten` | 本地有同名未跟踪文件，改名或删除 |
| `CONFLICT (content): Merge conflict in xxx` | 手动解决 → `add` → `commit` |
| `HEAD detached at xxx` | `git switch main` 回分支，或 `git switch -c 新分支` 保留修改 |
| 中文文件名显示成 `\345\210...` | `git config --global core.quotepath false` |
| `git log` 停住不动 | 进入了翻页模式，按 `q` 退出 |

---

## 17. 救命原则

1. **拿不准先 `git status`**
2. **勤 commit**：提交过的东西才受保护
3. **勤 push**：云端就是异地备份
4. **已推送用 `revert`，未推送才用 `reset`**
5. **`--hard`、`--force` 前三思**
6. **丢了先 `git reflog`**

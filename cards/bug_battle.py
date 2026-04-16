#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║               🐛  B U G  大 作 战  🐛                      ║
║                   Bug Battle — 控制台卡牌游戏               ║
║                                                              ║
║  基于 PMBOK 项目管理课堂展示设计                             ║
║  玩家扮演工程师，通过出牌消灭对手的 Bug 即获胜              ║
╚══════════════════════════════════════════════════════════════╝

规则说明:
  - 2人对战，每人场上初始 3 只 Bug
  - 每回合: 抽 1 张牌 → 选择出牌/弃牌 → 结算
  - 卡牌类型:
      🐛 Bug卡     — 给对手场上增加一只 Bug
      👨‍💻 工程师卡  — 对对手场上的 Bug 造成伤害
      🔧 工具卡    — 特殊效果 (回血/群攻/偷牌等)
  - 先消灭对手场上所有 Bug 的玩家获胜
"""

import random
import os
import sys
import time

# ══════════════════════════════════════════════════════════════
#  颜色与显示工具
# ══════════════════════════════════════════════════════════════

class Color:
    """ANSI 颜色码"""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_RED  = "\033[41m"
    BG_BLUE = "\033[44m"
    BG_GREEN= "\033[42m"
    BG_YELLOW="\033[43m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def colored(text, color):
    return f"{color}{text}{Color.RESET}"

def slow_print(text, delay=0.02):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def press_enter():
    input(colored("\n  ⏎ 按回车继续...", Color.DIM))

# ══════════════════════════════════════════════════════════════
#  卡牌定义
# ══════════════════════════════════════════════════════════════

class Card:
    def __init__(self, name, card_type, description, value=0, cost=0):
        self.name = name
        self.card_type = card_type   # "bug", "engineer", "tool"
        self.description = description
        self.value = value           # 攻击力/生命值/效果值
        self.cost = cost             # 能量消耗

    def display_icon(self):
        icons = {"bug": "🐛", "engineer": "👨‍💻", "tool": "🔧"}
        return icons.get(self.card_type, "❓")

    def display_color(self):
        colors = {"bug": Color.RED, "engineer": Color.BLUE, "tool": Color.GREEN}
        return colors.get(self.card_type, Color.WHITE)

    def __str__(self):
        icon = self.display_icon()
        color = self.display_color()
        if self.card_type == "bug":
            return colored(f"{icon} {self.name} [HP:{self.value}]", color)
        elif self.card_type == "engineer":
            return colored(f"{icon} {self.name} [ATK:{self.value}]", color)
        else:
            return colored(f"{icon} {self.name}", color)

    def detail_str(self):
        return f"{self}  {colored(self.description, Color.DIM)}"


class Bug:
    """场上的 Bug 实例"""
    def __init__(self, name, max_hp):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - dmg)

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def hp_bar(self, width=10):
        filled = int(self.hp / self.max_hp * width)
        bar = "█" * filled + "░" * (width - filled)
        if self.hp > self.max_hp * 0.5:
            color = Color.GREEN
        elif self.hp > self.max_hp * 0.25:
            color = Color.YELLOW
        else:
            color = Color.RED
        return f"🐛 {self.name:12s} {colored(bar, color)} {self.hp}/{self.max_hp}"

# ══════════════════════════════════════════════════════════════
#  牌库生成
# ══════════════════════════════════════════════════════════════

def create_deck():
    """生成 30 张卡牌的牌库"""
    cards = []

    # Bug 卡 (8 张) — 放到对手场上的 Bug
    bug_templates = [
        ("空指针异常",      "NullPointerException — 经典中的经典",     3),
        ("内存泄漏",        "Memory Leak — 悄无声息的杀手",           4),
        ("死循环",          "Infinite Loop — CPU 的噩梦",              3),
        ("数组越界",        "IndexOutOfBounds — 下标从 0 开始！",     2),
        ("并发死锁",        "Deadlock — 两个线程互相等待",            5),
        ("SQL注入",         "SQL Injection — 安全漏洞之王",           4),
        ("栈溢出",          "Stack Overflow — 不是那个网站",          3),
        ("编码乱码",        "Encoding Bug — 你好变成 ????",           2),
    ]
    for name, desc, hp in bug_templates:
        cards.append(Card(name, "bug", desc, value=hp))

    # 工程师卡 (12 张) — 攻击对手的 Bug
    engineer_templates = [
        ("初级程序员",      "刚入行的萌新，但也能修 Bug",             1),
        ("初级程序员",      "刚入行的萌新，但也能修 Bug",             1),
        ("中级开发者",      "有几年经验，Debug 效率不错",             2),
        ("中级开发者",      "有几年经验，Debug 效率不错",             2),
        ("中级开发者",      "有几年经验，Debug 效率不错",             2),
        ("高级工程师",      "经验丰富，手起刀落",                     3),
        ("高级工程师",      "经验丰富，手起刀落",                     3),
        ("架构师",          "看穿 Bug 本质，一击致命",                4),
        ("架构师",          "看穿 Bug 本质，一击致命",                4),
        ("全栈大神",        "前后端通吃，无所不能",                   5),
        ("CTO",             "技术之巅，Bug 见了绕道走",               6),
        ("Linus 本人",      "「Talk is cheap, show me the code」",    7),
    ]
    for name, desc, atk in engineer_templates:
        cards.append(Card(name, "engineer", desc, value=atk))

    # 工具卡 (10 张) — 特殊效果
    tool_templates = [
        ("Git Revert",      "回滚代码，治愈一只 Bug 2 点 HP",                "heal",     2),
        ("Git Revert",      "回滚代码，治愈一只 Bug 2 点 HP",                "heal",     2),
        ("Code Review",     "代码审查，对所有敌方 Bug 造成 1 点伤害",        "aoe",      1),
        ("Code Review",     "代码审查，对所有敌方 Bug 造成 1 点伤害",        "aoe",      1),
        ("单元测试",        "Unit Test — 精准定位，对一只 Bug 造成 3 点伤害", "snipe",    3),
        ("单元测试",        "Unit Test — 精准定位，对一只 Bug 造成 3 点伤害", "snipe",    3),
        ("CI/CD 流水线",    "自动化部署，额外抽 2 张牌",                     "draw",     2),
        ("CI/CD 流水线",    "自动化部署，额外抽 2 张牌",                     "draw",     2),
        ("Stack Overflow",  "上网搜答案，偷取对手 1 张手牌",                 "steal",    1),
        ("热修复 Hotfix",   "紧急补丁，直接消灭 HP ≤ 2 的 Bug",             "execute",  2),
    ]
    for name, desc, effect, val in tool_templates:
        cards.append(Card(name, "tool", desc, value=val))
        cards[-1].effect = effect

    random.shuffle(cards)
    return cards

# ══════════════════════════════════════════════════════════════
#  玩家类
# ══════════════════════════════════════════════════════════════

class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.is_ai = is_ai
        self.hand = []       # 手牌
        self.bugs = []       # 场上的 Bug
        self.energy = 3      # 每回合能量
        self.max_energy = 3

    def draw_card(self, deck, count=1):
        drawn = []
        for _ in range(count):
            if deck:
                card = deck.pop()
                self.hand.append(card)
                drawn.append(card)
        return drawn

    def has_bugs(self):
        return any(b.is_alive() for b in self.bugs)

    def alive_bugs(self):
        return [b for b in self.bugs if b.is_alive()]

    def clean_dead_bugs(self):
        dead = [b for b in self.bugs if not b.is_alive()]
        self.bugs = [b for b in self.bugs if b.is_alive()]
        return dead

# ══════════════════════════════════════════════════════════════
#  游戏主类
# ══════════════════════════════════════════════════════════════

class BugBattle:
    def __init__(self):
        self.deck = create_deck()
        self.discard = []
        self.players = []
        self.turn = 0
        self.game_over = False
        self.winner = None

    # ─── 初始化 ───
    def setup(self):
        clear_screen()
        self.print_title()

        print(colored("  ╔══════════════════════════════════════╗", Color.CYAN))
        print(colored("  ║         选 择 游 戏 模 式            ║", Color.CYAN))
        print(colored("  ╠══════════════════════════════════════╣", Color.CYAN))
        print(colored("  ║  [1]  👤 vs 🤖  人机对战            ║", Color.CYAN))
        print(colored("  ║  [2]  👤 vs 👤  双人对战            ║", Color.CYAN))
        print(colored("  ╚══════════════════════════════════════╝", Color.CYAN))

        while True:
            choice = input(colored("\n  请选择 (1/2): ", Color.YELLOW)).strip()
            if choice in ("1", "2"):
                break
            print(colored("  请输入 1 或 2", Color.RED))

        if choice == "1":
            name = input(colored("  请输入你的名字 (默认: Player): ", Color.YELLOW)).strip()
            if not name:
                name = "Player"
            self.players = [Player(name), Player("AI 机器人", is_ai=True)]
        else:
            name1 = input(colored("  玩家 1 名字 (默认: 玩家1): ", Color.YELLOW)).strip() or "玩家1"
            name2 = input(colored("  玩家 2 名字 (默认: 玩家2): ", Color.YELLOW)).strip() or "玩家2"
            self.players = [Player(name1), Player(name2)]

        # 每人初始 3 只 Bug
        starter_bugs = [
            ("语法错误",    2), ("逻辑错误",    3), ("运行时异常",  2),
            ("类型错误",    2), ("引用错误",    3), ("超时错误",    2),
        ]
        random.shuffle(starter_bugs)
        for i, player in enumerate(self.players):
            for j in range(3):
                name, hp = starter_bugs[i * 3 + j]
                player.bugs.append(Bug(name, hp))

        # 每人初始抽 4 张牌
        for player in self.players:
            player.draw_card(self.deck, 4)

        clear_screen()
        self.print_title()
        slow_print(colored("  ⚡ 游戏初始化完成！每位玩家获得 3 只初始 Bug 和 4 张手牌。", Color.GREEN))
        slow_print(colored("  ⚡ 先消灭对手所有 Bug 的玩家获胜！", Color.GREEN))
        press_enter()

    # ─── 主循环 ───
    def run(self):
        self.setup()
        while not self.game_over:
            for i, player in enumerate(self.players):
                if self.game_over:
                    break
                opponent = self.players[1 - i]
                self.turn += 1
                self.play_turn(player, opponent)
                self.check_win(player, opponent)

        self.show_result()

    # ─── 单回合 ───
    def play_turn(self, player, opponent):
        # 回合开始：恢复能量
        player.energy = player.max_energy

        # 抽牌阶段
        if self.deck:
            drawn = player.draw_card(self.deck, 1)
        else:
            # 洗入弃牌堆
            if self.discard:
                self.deck = self.discard[:]
                random.shuffle(self.deck)
                self.discard.clear()
                drawn = player.draw_card(self.deck, 1)
            else:
                drawn = []

        if player.is_ai:
            self.ai_turn(player, opponent, drawn)
        else:
            self.human_turn(player, opponent, drawn)

    # ─── 人类回合 ───
    def human_turn(self, player, opponent, drawn):
        clear_screen()
        self.print_turn_header(player)

        # 显示抽到的牌
        if drawn:
            print(colored(f"  📥 你抽到了: {drawn[0].detail_str()}", Color.CYAN))
        else:
            print(colored("  📥 牌库已空，未能抽牌", Color.DIM))
        print()

        # 显示战场
        self.print_battlefield(player, opponent)

        # 出牌循环
        while player.hand:
            print(colored(f"\n  ⚡ 剩余能量: {'🔋' * player.energy}{'  ' * (player.max_energy - player.energy)} ({player.energy}/{player.max_energy})", Color.YELLOW))
            print(colored("  ─── 你的手牌 ───", Color.BOLD))
            for idx, card in enumerate(player.hand):
                cost = self.get_card_cost(card)
                can_play = "✅" if cost <= player.energy else "❌"
                print(f"    [{idx + 1}] {can_play} {card.detail_str()}  (消耗 {cost} 能量)")

            print(f"    [0] 🏁 结束回合")
            print()

            choice = input(colored("  选择要出的牌 (编号): ", Color.YELLOW)).strip()

            if choice == "0":
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(player.hand):
                    card = player.hand[idx]
                    cost = self.get_card_cost(card)
                    if cost > player.energy:
                        print(colored("  ⚠️  能量不足！", Color.RED))
                        continue
                    success = self.play_card(player, opponent, card)
                    if success:
                        player.hand.pop(idx)
                        player.energy -= cost
                        self.discard.append(card)
                        # 清除死亡 Bug
                        dead = opponent.clean_dead_bugs()
                        for b in dead:
                            slow_print(colored(f"  💥 {b.name} 已被消灭！", Color.RED), 0.03)
                        dead = player.clean_dead_bugs()
                        for b in dead:
                            slow_print(colored(f"  💥 你的 {b.name} 已被消灭！", Color.RED), 0.03)

                        if not opponent.has_bugs():
                            return
                    else:
                        continue
                else:
                    print(colored("  ⚠️  无效编号", Color.RED))
            except ValueError:
                print(colored("  ⚠️  请输入数字", Color.RED))

            # 刷新战场
            print()
            self.print_battlefield(player, opponent)

        press_enter()

    # ─── AI 回合 ───
    def ai_turn(self, player, opponent, drawn):
        clear_screen()
        self.print_turn_header(player)

        if drawn:
            print(colored(f"  📥 {player.name} 抽了一张牌", Color.DIM))
        time.sleep(0.5)

        # AI 策略：优先出工程师卡攻击最低血的 Bug，然后出工具卡，最后出 Bug 卡
        played_any = True
        while played_any and player.hand:
            played_any = False

            # 按优先级排序手牌
            engineers = [c for c in player.hand if c.card_type == "engineer"]
            tools     = [c for c in player.hand if c.card_type == "tool"]
            bugs      = [c for c in player.hand if c.card_type == "bug"]

            # 尝试出工程师卡
            engineers.sort(key=lambda c: c.value, reverse=True)
            for card in engineers:
                cost = self.get_card_cost(card)
                if cost <= player.energy and opponent.alive_bugs():
                    player.hand.remove(card)
                    player.energy -= cost
                    # 选择血量最低的 Bug 攻击
                    target = min(opponent.alive_bugs(), key=lambda b: b.hp)
                    target.take_damage(card.value)
                    slow_print(colored(f"  ⚔️  {player.name} 派出 {card} 攻击 {target.name}，造成 {card.value} 点伤害！", Color.MAGENTA), 0.02)
                    self.discard.append(card)
                    dead = opponent.clean_dead_bugs()
                    for b in dead:
                        slow_print(colored(f"  💥 {b.name} 已被消灭！", Color.RED), 0.03)
                    played_any = True
                    break

            if not played_any:
                # 尝试出工具卡
                for card in tools:
                    cost = self.get_card_cost(card)
                    if cost <= player.energy:
                        effect = getattr(card, 'effect', None)
                        if effect == "aoe" and opponent.alive_bugs():
                            player.hand.remove(card)
                            player.energy -= cost
                            for bug in opponent.alive_bugs():
                                bug.take_damage(card.value)
                            slow_print(colored(f"  🔧 {player.name} 使用 {card}，对所有 Bug 造成 {card.value} 点伤害！", Color.MAGENTA), 0.02)
                            self.discard.append(card)
                            dead = opponent.clean_dead_bugs()
                            for b in dead:
                                slow_print(colored(f"  💥 {b.name} 已被消灭！", Color.RED), 0.03)
                            played_any = True
                            break
                        elif effect == "snipe" and opponent.alive_bugs():
                            player.hand.remove(card)
                            player.energy -= cost
                            target = min(opponent.alive_bugs(), key=lambda b: b.hp)
                            target.take_damage(card.value)
                            slow_print(colored(f"  🔧 {player.name} 使用 {card}，对 {target.name} 造成 {card.value} 点伤害！", Color.MAGENTA), 0.02)
                            self.discard.append(card)
                            dead = opponent.clean_dead_bugs()
                            for b in dead:
                                slow_print(colored(f"  💥 {b.name} 已被消灭！", Color.RED), 0.03)
                            played_any = True
                            break
                        elif effect == "draw":
                            player.hand.remove(card)
                            player.energy -= cost
                            new_cards = player.draw_card(self.deck, card.value)
                            slow_print(colored(f"  🔧 {player.name} 使用 {card}，抽了 {len(new_cards)} 张牌！", Color.MAGENTA), 0.02)
                            self.discard.append(card)
                            played_any = True
                            break
                        elif effect == "execute" and opponent.alive_bugs():
                            weak = [b for b in opponent.alive_bugs() if b.hp <= card.value]
                            if weak:
                                player.hand.remove(card)
                                player.energy -= cost
                                target = weak[0]
                                target.take_damage(target.hp)
                                slow_print(colored(f"  🔧 {player.name} 使用 {card}，直接消灭了 {target.name}！", Color.MAGENTA), 0.02)
                                self.discard.append(card)
                                dead = opponent.clean_dead_bugs()
                                for b in dead:
                                    slow_print(colored(f"  💥 {b.name} 已被消灭！", Color.RED), 0.03)
                                played_any = True
                                break
                        elif effect == "heal" and player.alive_bugs():
                            wounded = [b for b in player.alive_bugs() if b.hp < b.max_hp]
                            if wounded:
                                player.hand.remove(card)
                                player.energy -= cost
                                target = min(wounded, key=lambda b: b.hp)
                                target.heal(card.value)
                                slow_print(colored(f"  🔧 {player.name} 使用 {card}，恢复了 {target.name} {card.value} HP！", Color.MAGENTA), 0.02)
                                self.discard.append(card)
                                played_any = True
                                break
                        elif effect == "steal" and opponent.hand:
                            player.hand.remove(card)
                            player.energy -= cost
                            stolen = random.choice(opponent.hand)
                            opponent.hand.remove(stolen)
                            player.hand.append(stolen)
                            slow_print(colored(f"  🔧 {player.name} 使用 {card}，偷走了一张手牌！", Color.MAGENTA), 0.02)
                            self.discard.append(card)
                            played_any = True
                            break

            if not played_any:
                # 尝试出 Bug 卡
                for card in bugs:
                    cost = self.get_card_cost(card)
                    if cost <= player.energy:
                        player.hand.remove(card)
                        player.energy -= cost
                        opponent.bugs.append(Bug(card.name, card.value))
                        slow_print(colored(f"  🐛 {player.name} 放出 {card}，在对手场上生成了一只新 Bug！", Color.MAGENTA), 0.02)
                        self.discard.append(card)
                        played_any = True
                        break

            if not opponent.has_bugs():
                break

            time.sleep(0.3)

        print()
        self.print_battlefield(opponent, player)
        press_enter()

    # ─── 出牌逻辑 ───
    def play_card(self, player, opponent, card):
        if card.card_type == "bug":
            opponent.bugs.append(Bug(card.name, card.value))
            slow_print(colored(f"  🐛 你放出了 {card.name}，在对手场上生成了一只 Bug！", Color.RED), 0.03)
            return True

        elif card.card_type == "engineer":
            if not opponent.alive_bugs():
                print(colored("  ⚠️  对手场上没有 Bug 可攻击！", Color.RED))
                return False
            target = self.choose_target(opponent)
            if target is None:
                return False
            target.take_damage(card.value)
            slow_print(colored(f"  ⚔️  {card.name} 出击！对 {target.name} 造成 {card.value} 点伤害！", Color.BLUE), 0.03)
            return True

        elif card.card_type == "tool":
            effect = getattr(card, 'effect', None)
            return self.play_tool(player, opponent, card, effect)

        return False

    def play_tool(self, player, opponent, card, effect):
        if effect == "heal":
            wounded = [b for b in player.alive_bugs() if b.hp < b.max_hp]
            if not wounded:
                print(colored("  ⚠️  没有需要治疗的 Bug", Color.RED))
                return False
            print(colored("  选择要治疗的 Bug:", Color.GREEN))
            for i, bug in enumerate(wounded):
                print(f"    [{i + 1}] {bug.hp_bar()}")
            while True:
                try:
                    c = int(input(colored("  编号: ", Color.YELLOW)).strip()) - 1
                    if 0 <= c < len(wounded):
                        wounded[c].heal(card.value)
                        slow_print(colored(f"  💚 {wounded[c].name} 恢复了 {card.value} HP！", Color.GREEN), 0.03)
                        return True
                except (ValueError, IndexError):
                    pass
                print(colored("  ⚠️  无效选择", Color.RED))

        elif effect == "aoe":
            if not opponent.alive_bugs():
                print(colored("  ⚠️  对手场上没有 Bug！", Color.RED))
                return False
            for bug in opponent.alive_bugs():
                bug.take_damage(card.value)
            slow_print(colored(f"  🌊 Code Review 全体攻击！对所有 Bug 造成 {card.value} 点伤害！", Color.CYAN), 0.03)
            return True

        elif effect == "snipe":
            if not opponent.alive_bugs():
                print(colored("  ⚠️  对手场上没有 Bug！", Color.RED))
                return False
            target = self.choose_target(opponent)
            if target is None:
                return False
            target.take_damage(card.value)
            slow_print(colored(f"  🎯 单元测试精准打击！对 {target.name} 造成 {card.value} 点伤害！", Color.CYAN), 0.03)
            return True

        elif effect == "draw":
            new = player.draw_card(self.deck, card.value)
            slow_print(colored(f"  📥 CI/CD 流水线启动！你抽了 {len(new)} 张牌！", Color.CYAN), 0.03)
            return True

        elif effect == "steal":
            if not opponent.hand:
                print(colored("  ⚠️  对手没有手牌可偷！", Color.RED))
                return False
            stolen = random.choice(opponent.hand)
            opponent.hand.remove(stolen)
            player.hand.append(stolen)
            slow_print(colored(f"  🕵️  你从 Stack Overflow 上偷到了 {stolen}！", Color.CYAN), 0.03)
            return True

        elif effect == "execute":
            weak = [b for b in opponent.alive_bugs() if b.hp <= card.value]
            if not weak:
                print(colored(f"  ⚠️  没有 HP ≤ {card.value} 的 Bug 可以消灭！", Color.RED))
                return False
            if len(weak) == 1:
                target = weak[0]
            else:
                print(colored("  选择要消灭的 Bug:", Color.RED))
                for i, bug in enumerate(weak):
                    print(f"    [{i + 1}] {bug.hp_bar()}")
                while True:
                    try:
                        c = int(input(colored("  编号: ", Color.YELLOW)).strip()) - 1
                        if 0 <= c < len(weak):
                            target = weak[c]
                            break
                    except (ValueError, IndexError):
                        pass
                    print(colored("  ⚠️  无效选择", Color.RED))
            target.take_damage(target.hp)
            slow_print(colored(f"  ⚡ 热修复上线！{target.name} 被直接消灭！", Color.CYAN), 0.03)
            return True

        return False

    def choose_target(self, opponent):
        bugs = opponent.alive_bugs()
        if len(bugs) == 1:
            return bugs[0]
        print(colored("  选择要攻击的 Bug:", Color.RED))
        for i, bug in enumerate(bugs):
            print(f"    [{i + 1}] {bug.hp_bar()}")
        while True:
            raw = input(colored("  编号 (输入 0 取消): ", Color.YELLOW)).strip()
            if raw == "0":
                return None
            try:
                c = int(raw) - 1
                if 0 <= c < len(bugs):
                    return bugs[c]
            except (ValueError, IndexError):
                pass
            print(colored("  ⚠️  无效选择", Color.RED))

    def get_card_cost(self, card):
        if card.card_type == "bug":
            return 1
        elif card.card_type == "engineer":
            if card.value <= 2:
                return 1
            elif card.value <= 4:
                return 2
            else:
                return 3
        else:
            return 2

    # ─── 胜负判定 ───
    def check_win(self, current, opponent):
        if not opponent.has_bugs():
            self.game_over = True
            self.winner = current

    # ─── 显示函数 ───
    def print_title(self):
        title = """
  ╔══════════════════════════════════════════════════════════════╗
  ║                                                              ║
  ║     ██████╗ ██╗   ██╗ ██████╗                               ║
  ║     ██╔══██╗██║   ██║██╔════╝                               ║
  ║     ██████╔╝██║   ██║██║  ███╗                              ║
  ║     ██╔══██╗██║   ██║██║   ██║                              ║
  ║     ██████╔╝╚██████╔╝╚██████╔╝                              ║
  ║     ╚═════╝  ╚═════╝  ╚═════╝                               ║
  ║                                                              ║
  ║              🐛  大 作 战  —  Bug Battle  🐛                ║
  ║                                                              ║
  ║       玩家扮演工程师，出牌消灭对手的 Bug 即获胜！           ║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝
"""
        print(colored(title, Color.CYAN))

    def print_turn_header(self, player):
        icon = "🤖" if player.is_ai else "👤"
        header = f"  ══════════  第 {self.turn} 回合 · {icon} {player.name} 的回合  ══════════"
        print(colored(header, Color.BOLD + Color.YELLOW))
        print(colored(f"  牌库剩余: {len(self.deck)} 张  |  弃牌堆: {len(self.discard)} 张", Color.DIM))
        print()

    def print_battlefield(self, player, opponent):
        print(colored(f"  ┌─── 🏠 {opponent.name} 的 Bug ({len(opponent.alive_bugs())} 只存活) ───", Color.RED))
        if opponent.alive_bugs():
            for bug in opponent.alive_bugs():
                print(f"  │  {bug.hp_bar()}")
        else:
            print(colored("  │  (空)", Color.DIM))
        print(colored("  ├────────────────────────────────────────", Color.DIM))
        print(colored(f"  └─── 🏠 {player.name} 的 Bug ({len(player.alive_bugs())} 只存活) ───", Color.BLUE))
        if player.alive_bugs():
            for bug in player.alive_bugs():
                print(f"       {bug.hp_bar()}")
        else:
            print(colored("       (空)", Color.DIM))
        print()

    def show_result(self):
        clear_screen()
        if self.winner:
            result = f"""
  ╔══════════════════════════════════════════════════════════════╗
  ║                                                              ║
  ║                  🎉  游 戏 结 束  🎉                       ║
  ║                                                              ║
  ║              🏆  {self.winner.name:^12s} 获得胜利！              ║
  ║                                                              ║
  ║              总回合数: {self.turn:^4d}                            ║
  ║                                                              ║
  ╚══════════════════════════════════════════════════════════════╝
"""
            print(colored(result, Color.GREEN + Color.BOLD))

            # 战报
            print(colored("  ── 📊 战斗报告 ──", Color.CYAN))
            for p in self.players:
                icon = "🏆" if p == self.winner else "💀"
                print(colored(f"  {icon} {p.name}", Color.BOLD))
                print(colored(f"      剩余手牌: {len(p.hand)} 张", Color.DIM))
                alive = len(p.alive_bugs())
                total = len(p.bugs) + len([1 for _ in range(3)])  # 初始3只
                print(colored(f"      存活 Bug: {alive} 只", Color.DIM))
                print()

        slow_print(colored("\n  感谢游玩《Bug 大作战》！再见！👋\n", Color.CYAN))

# ══════════════════════════════════════════════════════════════
#  入口
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        game = BugBattle()
        game.run()
    except KeyboardInterrupt:
        print(colored("\n\n  👋 游戏已退出，下次再见！\n", Color.CYAN))
        sys.exit(0)

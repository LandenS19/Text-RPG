import random
import pygame
import threading
import time
import sys


pygame.mixer.init()

# ANSI color codes
COLOR_RESET = "\033[0m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_BLUE = "\033[94m"
COLOR_PURPLE = "\033[95m"
COLOR_CYAN = "\033[96m"
COLOR_WHITE = "\033[97m"
COLOR_ORANGE = "\033[38;5;208m"


def fireball_effect(target):
    if target:
        damage = random.randint(10, 30)
        target.health -= damage
        word_by_word(f"The Fireball hits {target.name} for {damage} damage!")
    else:
        word_by_word("No target for Fireball.")

def heal_effect(target):
    if target:
        heal_amount = random.randint(15, 25)
        target.health = min(target.max_health, target.health + heal_amount)
        word_by_word(f"{target.name} is healed for {heal_amount} health!")
    else:
        word_by_word("No target to heal.")

def shield_effect(target):
    if target:
        boost = 5
        target.defense += boost
        word_by_word(f"{target.name}'s defense increased by {boost}!")
    else:
        word_by_word("No target for Shield.")



PLAYER_CLASSES = {
    "Warrior": {"max_health": 120, "attack_power": 18, "defense": 7, "crit_chance": 15, "mana": 30, "magic_attack_power": 5, "agility": 10},
    "Mage": {"max_health": 80, "attack_power": 12, "defense": 5, "crit_chance": 15, "mana": 100, "magic_attack_power": 20, "agility": 10},
    "Rogue": {"max_health": 100, "attack_power": 15, "defense": 6, "crit_chance": 25, "mana": 50, "magic_attack_power": 10, "agility": 20},
    "Default": {"max_health": 100, "attack_power": 10, "defense": 5, "crit_chance": 15, "mana": 50, "magic_attack_power": 10, "agility": 10},
}

SPELLS = {
    "Fireball": {
        "mana_cost": 20,
        "effect": lambda target: fireball_effect(target),
        "description": COLOR_RED + "A powerful fire spell that deals 10-30 damage to a single enemy." + COLOR_RESET
    },
    "Heal": {
        "mana_cost": 15,
        "effect": lambda target: heal_effect(target),
        "description": COLOR_GREEN + "A healing spell that restores 15-25 health to a single target." + COLOR_RESET
    },
    "Shield": {
        "mana_cost": 10,
        "effect": lambda target: shield_effect(target),
        "description": COLOR_CYAN + "Increases target's defense temporarily." + COLOR_RESET
    },
}

STARTING_SPELLS = {
    "Warrior": ["Shield"],
    "Mage": ["Fireball", "Heal"],
    "Rogue": ["Heal"],
    "Default": ["Heal"]
}

# Player class
class Player:
    def __init__(self, name, player_class="Default"):
        self.name = name
        
        # Ensure the class exists in the configuration
        if player_class not in PLAYER_CLASSES:
            raise ValueError(f"Invalid class: {player_class}")
        
        # Load stats from configuration
        stats = PLAYER_CLASSES[player_class]
        self.max_health = stats["max_health"]
        self.health = self.max_health
        self.attack_power = stats["attack_power"]
        self.defense = stats["defense"]
        self.max_defense = self.defense
        self.agility = stats["agility"]
        self.crit_chance = stats["crit_chance"]  # Critical chance percentage
        self.mana = stats.get("mana", 50)
        self.magic_attack_power = stats.get("magic_attack_power", 10)
        self.max_mana = self.mana
        self.spells = []  # List of learned spell names


        # Other attributes
        self.crit_damage = self.attack_power / 2
        self.level = 1
        self.xp = 0
        self.items = ["Healing Potion", "Health Upgrade", "Attack Upgrade", "Defense Upgrade", "Crit Chance Upgrade", "Mana Upgrade", "Magic Attack Power Upgrade", "Agility Upgrade"]
        self.inventory = {
            "Healing Potion": 5,
            "Health Upgrade": 0,
            "Attack Upgrade": 0,
            "Defense Upgrade": 0,
            "Crit Chance Upgrade": 0,
            "Mana Upgrade": 0,
            "Magic Attack Power Upgrade": 0,
            "Agility Upgrade": 0,
        }  # Add 5 healing potions to the inventory and initialize other upgrades
        self.level_up = 100
        self.health_upgrades = 0

    def attack(self):
        damage = random.randint(1, self.attack_power)
        if random.randint(1, 100) <= self.crit_chance:
            word_by_word(COLOR_RED + f"Critical Hit! {self.name} deals {damage + self.crit_damage:.0f} damage!" + COLOR_RESET)
            return damage + self.crit_damage
        return damage

    def defend(self):
        return random.randint(1, self.defense)

    def add_to_inventory(self, item, quantity=1):
        item_sound = pygame.mixer.Sound("Sounds/item_pickup.mp3")
        item_sound.play()
        if item in self.inventory:
            self.inventory[item] += quantity
        else:
            self.inventory[item] = quantity

    def show_inventory(self):
        global a
        word_by_word(f"Inventory of {self.name}:")
        a = 1
        for item, quantity in self.inventory.items():
            word_by_word(f"{item} x{quantity} ({a}) ")
            a += 1

    def heal(self):
        self.health = self.max_health
        word_by_word(COLOR_GREEN + f"{self.name} has been completely healed." + COLOR_RESET)

    def health_potion(self):
        self.health = self.health + 15
        if self.health > self.max_health:
            self.health = self.max_health
    
    def stats(self):
        word_by_word(
            COLOR_GREEN + f"Max Health : {self.max_health}"
            + COLOR_RED + f"\nCurrent Health : {self.health}"
            + COLOR_ORANGE + f"\nCurrent Attack Power : {self.attack_power}"
            + COLOR_CYAN + f"\nCurrent Defense : {self.defense}"
            + COLOR_YELLOW + f"\nCritical Chance : {self.crit_chance}%"
            + COLOR_BLUE + f"\nMana : {self.mana}/{self.max_mana}"
            + COLOR_PURPLE + f"\nMagic Attack Power : {self.magic_attack_power}"
            + COLOR_CYAN + f"\nAgility : {self.agility}"
            + COLOR_RESET
        )

    def learn_spell(self, spell_name):
        """Add a spell to the player's spellbook."""
        if spell_name in SPELLS:
            if spell_name not in self.spells:
                self.spells.append(spell_name)
                word_by_word(f"{self.name} learned the spell: {spell_name}!")
            else:
                word_by_word(f"{self.name} already knows the spell: {spell_name}.")
        else:
            word_by_word(f"The spell {spell_name} does not exist.")

    def cast_spell(self, spell_name, target=None):
        """Cast a spell if the player has enough mana."""
        if spell_name in self.spells:
            spell = SPELLS[spell_name]
            if self.mana >= spell["mana_cost"]:
                self.mana -= spell["mana_cost"]
                word_by_word(f"{self.name} casts {spell_name}!")
                spell["effect"](target)  # Apply the spell's effect
            else:
                word_by_word(f"Not enough mana to cast {spell_name}.")
        else:
            word_by_word(f"{self.name} doesn't know the spell: {spell_name}.")

    def regenerate_mana(self, amount):
        """Regenerate mana up to the maximum."""
        self.mana = min(self.max_mana, self.mana + amount)
        word_by_word(f"{self.name} regenerated {amount} mana.")

    def rest(self):
        self.heal()
        self.regenerate_mana(self.max_mana)

# Enemy class
class Enemy:
    def __init__(self, name, base_health, base_attack_power, xp_reward, level):
        self.name = name
        self.base_health = base_health
        self.base_attack_power = base_attack_power
        self.base_xp_reward = xp_reward
        self.level = level
        self.health = base_health + (level - 1) * 5
        self.attack_power = base_attack_power + (level - 1) * 2
        self.xp_reward = base_xp_reward + (level - 1) * 2

    def attack(self):
        return random.randint(1, self.attack_power)

    def take_damage(self, damage):
        self.health -= damage

# Function to play background music
def background_music(player):
    pygame.mixer.music.load("Sounds/moonlit_melody.mp3")
    pygame.mixer.music.play(-1)

# Function to check player's health and play heartbeat sound if health is low
def check_health_warning(player):
    heartbeat_sound = pygame.mixer.Sound("Sounds/heartbeat.mp3")
    heartbeat_playing = False

    while player.health > 0:
        if player.health < 15:
            if not heartbeat_playing:
                # If the heartbeat sound is not already playing, start it
                heartbeat_sound.play()
                heartbeat_playing = True
                # Restart background music if stopped
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
        else:
            if heartbeat_playing:
                # If the heartbeat sound is currently playing, stop it
                heartbeat_sound.stop()
                heartbeat_playing = False
        
        pygame.time.wait(1000)  # Check every second

# Function to print text with a typing effect
def word_by_word(text, delay=0.1):
    """Prints text word by word with a typing effect."""
    lines = text.split('\n')  # Split the text into lines
    for line in lines:
        words = line.split()
        for word in words:
            sys.stdout.write(word + ' ')
            sys.stdout.flush()
            time.sleep(delay)
        print()  # Move to the next line after the text

# Function to get user input with a typing effect for the prompt
def get_input_with_typing(prompt, delay=0.05):
    """Prints a prompt with a typing effect and gets user input."""
    word_by_word(prompt, delay)
    return input()  # Get the user input after the prompt is displayed

# Define locations and their possible encounters
locations = {
    "Forest": [("Goblin", 20, 5, 10),
               ("Wolf", 30, 8, 15),
               ("Bear", 40, 10, 20)],
    "Cave": [("Bat", 10, 3, 5),
             ("Spider", 15, 5, 8),
             ("Troll", 30, 10, 20)],
    "Castle": [("Guard", 40, 10, 20),
               ("Knight", 50, 15, 25),
               ("Dragon", 80, 20, 50)],
    "Mountain": [("Eagle", 25, 7, 12),
                 ("Yeti", 45, 12, 25),
                 ("Rock Golem", 60, 18, 35)],
    "Desert": [("Scorpion", 35, 9, 15),
               ("Nomad", 40, 11, 20),
               ("Sand Worm", 55, 14, 30)],
    "Underground Lake": [("Giant Crab", 30, 8, 12),
                         ("Fishman", 35, 10, 18),
                         ("Kraken", 70, 20, 40)],
    "Arctic": [("Snowman", 15, 8, 10),
               ("Polar Bear", 35, 10, 25),
               ("Ice Golem", 50, 17, 40)]
}

# Start of the game
player_name = get_input_with_typing("Enter your name: ")
word_by_word("Choose your class:")
for index, (class_name, stats) in enumerate(PLAYER_CLASSES.items(), start=1):
    word_by_word(f"{index}. {class_name}")

while True:
    try:
        choice = int(get_input_with_typing("Enter the number of your chosen class: ")) - 1
        class_names = list(PLAYER_CLASSES.keys())
        
        if 0 <= choice < len(class_names):
            selected_class = class_names[choice]
            word_by_word(f"You have chosen: {selected_class}\n")
            break
        else:
            word_by_word("Invalid choice. Please select a valid number.")
    except ValueError:
        word_by_word("Invalid input. Please enter a number.")

player = Player(name=player_name, player_class=selected_class)
word_by_word(COLOR_GREEN + "Your journey begins..." + COLOR_RESET)
if selected_class == "Warrior":
    for spell in STARTING_SPELLS["Warrior"]:
        player.learn_spell(spell)
elif selected_class == "Mage":
    for spell in STARTING_SPELLS["Mage"]:
        player.learn_spell(spell)
elif selected_class == "Rogue":
    for spell in STARTING_SPELLS["Rogue"]:
        player.learn_spell(spell)
else:
    for spell in STARTING_SPELLS["Default"]:
        player.learn_spell(spell)


    

# After initializing player and pygame.mixer:
music_thread = threading.Thread(target=background_music, args=(player,))
music_thread.daemon = True
music_thread.start()

health_thread = threading.Thread(target=check_health_warning, args=(player,))
health_thread.daemon = True
health_thread.start()

current_location = "Forest"
level_range = 2

# Main game loop
while player.health > 0:
    word_by_word(f"You are currently in the " + COLOR_GREEN + f"{current_location}." + COLOR_RESET)
    action = get_input_with_typing("Do you want to (e)xplore, (i)nspect inventory, (r)est, (v)iew stats, go to a (n)ew location, or (q)uit?")

    if action.lower() == "e":
        # Explore the current location
        if random.random() < 0.15:
            item = random.choice(player.items)
            player.add_to_inventory(item)
            word_by_word(COLOR_CYAN + f"{player.name} found a {item}" + COLOR_RESET)
        else:
            encounter_name, base_health, base_attack_power, base_xp_reward = random.choice(locations[current_location])
            enemy_level = random.randint(player.level, level_range)  # Cap enemy level at 5
            enemy = Enemy(encounter_name, base_health, base_attack_power, base_xp_reward, enemy_level)

            word_by_word(f"You encounter a level " + COLOR_CYAN + f"{enemy.level}"
                          + COLOR_RESET + COLOR_RED + f" {enemy.name}" + COLOR_RESET 
                          + f" with " + COLOR_RED + f"{enemy.health}" + COLOR_RESET + " health!")

            # Battle loop
            while enemy.health > 0 and player.health > 0:
                player_choice = get_input_with_typing("Do you want to (a)ttack, (r)un, or (i)nspect inventory? ")

                if player_choice.lower() == "a":
                    crit_roll = random.randint(0,100)
                    attack_type = get_input_with_typing("(S)pell or (N)ormal attack?")

                    if attack_type.lower() == "s":
                        if player.mana > 0:
                            if player.spells:
                                word_by_word("Choose a spell to cast:")
                                for index, spell_name in enumerate(player.spells, start=1):
                                    word_by_word(f"{index}. {spell_name} - {SPELLS[spell_name]['description']}")

                                while True:
                                    try:
                                        spell_choice = int(get_input_with_typing("Enter the number of the spell you want to cast: ")) - 1
                                        if 0 <= spell_choice < len(player.spells):
                                            enemy_health_before = enemy.health
                                            selected_spell = player.spells[spell_choice]
                                            if selected_spell == "Fireball":
                                                player.cast_spell(selected_spell, enemy)
                                            elif selected_spell == "Heal":
                                                player.cast_spell(selected_spell, player)
                                            elif selected_spell == "Shield":
                                                player.cast_spell(selected_spell, player)
                                            word_by_word(f"{enemy.name} health: {enemy_health_before} -> {enemy.health}")
                                            break
                                        else:
                                            word_by_word("Invalid choice. Please select a valid number.")
                                    except ValueError:
                                        word_by_word("Invalid input. Please enter a number.")
                            else:
                                word_by_word("You don't know any spells.")
                        else:
                            word_by_word("Not enough mana to cast a spell.")

                    elif attack_type.lower() == "n":
                        # Player chooses to attack
                        if  crit_roll < player.crit_chance:
                            player_damage = (player.attack() + (player.crit_damage))
                            enemy_health_before = enemy.health
                            enemy.take_damage(player_damage)
                            crit_sound = pygame.mixer.Sound("Sounds/crit.mp3")
                            if not pygame.mixer.music.get_busy():
                                pygame.mixer.music.play(-1)  # Restart background music if stopped
                            crit_sound.play()
                            word_by_word(COLOR_RED + "CRIT! " + COLOR_GREEN + f"{player.name}" + COLOR_CYAN + f"({player.level})" + COLOR_RESET + f" attacks {enemy.name} for " + COLOR_RED + f"{player_damage} damage." + COLOR_RESET)
                            word_by_word(f"{enemy.name} health: {enemy_health_before} -> {max(0, enemy.health)}")
                        else:
                            player_damage = player.attack()
                            enemy_health_before = enemy.health
                            enemy.take_damage(player_damage)
                            attack_sound = pygame.mixer.Sound("Sounds/attack.mp3")
                            if not pygame.mixer.music.get_busy():
                                pygame.mixer.music.play(-1)  # Restart background music if stopped
                            attack_sound.play()    
                            word_by_word(COLOR_GREEN + f"{player.name}" + COLOR_CYAN + f"({player.level})" + COLOR_RESET + f" attacks {enemy.name} for " + COLOR_RED + f"{player_damage} damage." + COLOR_RESET)
                            word_by_word(f"{enemy.name} health: {enemy_health_before} -> {enemy.health}")
                    

                    # Enemy's turn
                    if enemy.health > 0:
                        enemy_damage = enemy.attack()
                        player_health_before = player.health
                        blocked = player.defend()
                        player_health_after = player_health_before - max(0, enemy_damage - blocked)
                        player.health = player_health_after
                        word_by_word(
                            COLOR_RED + f"{enemy.name}" + COLOR_RESET + f" attacks {player.name} for " + COLOR_RED + f"{enemy_damage} damage." + COLOR_RESET + COLOR_CYAN +f" {player.name}" + COLOR_RESET + " blocks " + COLOR_BLUE + f"{blocked}" + COLOR_RESET + " damage. For a total of " + COLOR_RED + f"{max(0, enemy_damage - blocked)}" + COLOR_RESET + " damage!")
                        word_by_word(f"{player.name} health: {player_health_before} -> {player_health_after}")
                    

                elif player_choice.lower() == "r":
                    # Player chooses to run
                    word_by_word("You attempt to run away.")
                    if random.uniform(0, player.agility) > random.uniform(0, 10 * enemy.level):
                        word_by_word(COLOR_GREEN + "You successfully flee!" + COLOR_RESET)
                        break
                    else:
                        word_by_word(COLOR_RED + "You failed to escape!" + COLOR_RESET)
                        enemy_damage = enemy.attack()
                        player_health_before = player.health
                        blocked = player.defend()
                        player_health_after = player_health_before - max(0, enemy_damage)
                        player.health = player_health_after
                        word_by_word(
                            COLOR_RED + f"{enemy.name}" + COLOR_RESET + f" attacks {player.name} for " + COLOR_RED + f"{enemy_damage} damage." + COLOR_RESET)
                        word_by_word(f"{player.name} health: {player_health_before} -> {player_health_after}")

                elif player_choice.lower() == "i":
                    y = True
                    while y:
                            try:
                                # Inspect inventory
                                player.show_inventory()
                                item_use = get_input_with_typing(f"Return (9)\n:")
                                item_use = int(item_use)  # Convert input to integer

                                item_actions = {
                                    1: ("Healing Potion", player.health_potion, 15, "restored 15 health"),
                                    2: ("Health Upgrade", lambda: setattr(player, 'max_health', player.max_health + 10), None, "increased max health by 10"),
                                    3: ("Attack Upgrade", lambda: setattr(player, 'attack_power', player.attack_power + 5), None, "increased attack power by 5"),
                                    4: ("Defense Upgrade", lambda: setattr(player, 'defense', player.defense + 2), None, "increased defense by 2"),
                                    5: ("Crit Chance Upgrade", lambda: setattr(player, 'crit_chance', player.crit_chance + 2), None, "increased crit chance by 2"),
                                    6: ("Mana Upgrade", lambda: setattr(player, 'max_mana', player.max_mana + 10), None, "increased max mana by 10"),
                                    7: ("Magic Attack Power Upgrade", lambda: setattr(player, 'magic_attack_power', player.magic_attack_power + 5), None, "increased magic attack power by 5"),
                                    8: ("Agility Upgrade", lambda: setattr(player, 'agility', player.agility + 2), None, "increased agility by 2"),
                                }

                                if item_use == 9:
                                    word_by_word("")
                                    y = False
                                elif item_use in item_actions:
                                    item_name, action, heal_amount, message = item_actions[item_use]
                                    if player.inventory.get(item_name, 0) > 0:
                                        action()
                                        if heal_amount:
                                            player.health = min(player.max_health, player.health + heal_amount)
                                        player.inventory[item_name] -= 1
                                        word_by_word(f"{player.name} used a {item_name} and {message}.")
                                        word_by_word(f"Current Health : {player.health}")
                                        y = False
                                    else:
                                        word_by_word("Invalid. Either you don't have that item or that isn't an option")
                                else:
                                    word_by_word("Invalid. Either you don't have that item or that isn't an option")
                            except ValueError:
                                word_by_word("Invalid input. Please enter a number.")
                                continue
                    enemy_damage = enemy.attack()
                    blocked = player.defend()
                    player_health_before = player.health
                    player_health_after = player_health_before - max(0, enemy_damage - blocked)
                    player.health = player_health_after
                    word_by_word(
                        COLOR_RED + f"{enemy.name}" + COLOR_RESET + f" attacks {player.name} for " + COLOR_RED + f"{enemy_damage} damage." + COLOR_RESET)
                    word_by_word(f"{player.name} health: {player_health_before} -> {player_health_after}")
            # Player wins the battle
            if enemy.health <= 0:
                player.xp += enemy.xp_reward
                word_by_word(f"{player.name} defeated the {enemy.name} and gained {enemy.xp_reward} XP.")
                word_by_word("Total XP:" + COLOR_BLUE + f"{player.xp}" + COLOR_RESET)
                if random.random() > 0.5:
                    item = random.choice(player.items)
                    player.add_to_inventory(item)
                    word_by_word(COLOR_CYAN + f"{player.name} gained a {item}" + COLOR_RESET)
                player.defense = player.max_defense

                # Check for level up
                if player.xp >= player.level_up:
                    level_up_sound = pygame.mixer.Sound("Sounds/level_up.mp3")
                    if not pygame.mixer.music.get_busy():
                        pygame.mixer.music.play(-1)  # Restart background music if stopped
                    level_up_sound.play()  
                    player.level += 1
                    player.xp = 0
                    player.level_up += player.level * (player.level_up * .05)
                    word_by_word(COLOR_BLUE + f"{player.name} leveled up to level {player.level}!" + COLOR_RESET)
                    player.rest()
                    level_range += 5
                    x = True
                    while x == True:
                        try:
                            leveled_attribute = get_input_with_typing(f"What attribute would you like to increase?"
                                              f"\n(h)ealth : {player.max_health}"
                                              f"\n(a)ttack Power : {player.attack_power}"
                                              f"\n(d)efense : {player.defense}"
                                              f"\n(c)rit Chance : {player.crit_chance}"
                                              f"\n(m)ana : {player.max_mana}"
                                              f"\n(M)agic Attack Power : {player.magic_attack_power}"
                                              f"\n(a)gility : {player.agility}\n")
                            if leveled_attribute == "h":
                                player.max_health += 10
                                player.health_upgrades += 1
                                player.stats()
                                time.sleep(1)
                                x = False
                                player.health = player.max_health
                            elif leveled_attribute == "a":
                                player.attack_power += 5
                                player.stats()
                                time.sleep(1)
                                x = False
                            elif leveled_attribute == "d":
                                player.defense += 2
                                player.stats()
                                time.sleep(1)
                                x = False
                            elif leveled_attribute == "c":
                                player.crit_chance += 2
                                player.stats()
                                time.sleep(1)
                                x = False
                            elif leveled_attribute == "m":
                                player.max_mana += 10
                                player.stats()
                                time.sleep(1)
                                x = False
                            elif leveled_attribute == "M":
                                player.magic_attack_power += 5
                                player.stats()
                                time.sleep(1)
                                x = False
                            elif leveled_attribute == "a":
                                player.agility += 2
                                player.stats()
                                time.sleep(1)
                                x = False
                            else:
                                word_by_word(COLOR_RED + "Invalid Input" + COLOR_RESET)
                        except:
                            word_by_word(COLOR_RED + "Ivalid Input!")
                            continue

    elif action.lower() == "r":
        # Rest and restore some health
        player.rest()

    elif action.lower() == "i":
        y = True
        while y == True:
            try:
                # Inspect inventory
                player.show_inventory()
                item_use = get_input_with_typing(f"Return (9)\n")
                item_use = int(item_use)  # Convert input to integer

                item_actions = {
                    1: ("Healing Potion", player.health_potion, 15, "restored 15 health"),
                    2: ("Health Upgrade", lambda: setattr(player, 'max_health', player.max_health + 10), None, "increased max health by 10"),
                    3: ("Attack Upgrade", lambda: setattr(player, 'attack_power', player.attack_power + 5), None, "increased attack power by 5"),
                    4: ("Defense Upgrade", lambda: setattr(player, 'defense', player.defense + 2), None, "increased defense by 2"),
                    5: ("Crit Chance Upgrade", lambda: setattr(player, 'crit_chance', player.crit_chance + 2), None, "increased crit chance by 2"),
                    6: ("Mana Upgrade", lambda: setattr(player, 'max_mana', player.max_mana + 10), None, "increased max mana by 10"),
                    7: ("Magic Attack Power Upgrade", lambda: setattr(player, 'magic_attack_power', player.magic_attack_power + 5), None, "increased magic attack power by 5"),
                    8: ("Agility Upgrade", lambda: setattr(player, 'agility', player.agility + 2), None, "increased agility by 2"),
                }

                if item_use == 9:
                    word_by_word("")
                    y = False
                elif item_use in item_actions:
                    item_name, action, heal_amount, message = item_actions[item_use]
                    if player.inventory.get(item_name, 0) > 0:
                        action()
                        if heal_amount:
                            player.health = min(player.max_health, player.health + heal_amount)
                        player.inventory[item_name] -= 1
                        word_by_word(f"{player.name} used a {item_name} and {message}.")
                        word_by_word(f"Current Health : {player.health}")
                        y = False
                    else:
                        word_by_word("Invalid. Either you don't have that item or that isn't an option")
                else:
                    word_by_word("Invalid. Either you don't have that item or that isn't an option")
            except ValueError:
                word_by_word("Invalid input. Please enter a number.")
                continue
    
    elif action.lower() == "v":
        # View Player Stats
        player.stats()

    elif action.lower() == "n":
        # Go to a new location
        current_location = random.choice(list(locations.keys()))
    
    elif action.lower() == "q":
        break

if player.health <= 0:
    word_by_word(COLOR_RED + "Game over. You have been defeated." + COLOR_RESET)
else:
    word_by_word(COLOR_GREEN + "Thanks for playing!" + COLOR_RESET)

pygame.mixer.stop()
pygame.quit()
sys.exit()

'''
Open Questions:
    - Determination of primary effect if multiple of a brew's effects are tied for highest value
    - Do Physician/Benefactor/Poisoner perks apply to eating ingredients?
    - Could effect name and value be equal, but magnitude/duration *not* be equal?
'''
%%time
#"helper functions"
#still have to get the effectsDict Keywords into a proper list/set?
physicianKeywords = set(["MagicAlchRestoreHealth", "MagicAlchRestoreMagicka", "MagicAlchRestoreStamina"])
AlchemistRank = 0 #Alchemistperk, ranks 1 through 5 available
PhysicianRank = 0 #Physician perk, 0 if not taken, 1 if taken
BenefactorRank = 0 #Benefactor perk, 0 if not taken, 1 if taken
PoisonerRank = 0 #Poisoner perk, 0 if not taken, 1 if taken
Alchemy = 0 #Alchemy Skill level
AlchemyMod = 0 #Fortify Alchemy in %

NoDurationList = ["Cure Disease", "Cure Poison", "Restore Health", "Restore Magicka", "Restore Stamina"]
NoMagnitudeList = ["Invsibility", "Paralysis", "Waterbreathing"]
PowerAffectsDurationList = ["Damage Magicka Regen", "Slow", "Damage Stamina Regen", "Invisibility", "Paralysis", "Waterbreathing", "Light", "Night Eye", "Spell Absorption"]

def Potionlike(effectName):
    return "MagicAlchBeneficial" in effectsDict[effectName]["Keyword(s)"] or effectName == "Resist Poison"

def Poisonlike(effectName):
    return "MagicAlchHarmful" in effectsDict[effectName]["Keyword(s)"] or effectName == "Fear" or effectName == "Frenzy"

def AlchemistPerk():
    return AlchemistRank*20

def PhysicianPerk(effect):
    if PhysicianRank==1:
        effectName = effect["Effect Name"]
        effectKeywords = set(effectsDict[effectName]["Keyword(s)"])
        physicianKeywords = set(["MagicAlchRestoreHealth", "MagicAlchRestoreMagicka", "MagicAlchRestoreStamina"])
        if len(effectKeywords.intersection(physicianKeywords)) > 0:
            return 25
    return 0

def BenefactorPerk(effect, isPoison):
    if BenefactorRank == 1 and not isPoison:
        effectName = effect["Effect Name"]
        effectKeywords = set(effectsDict[effectName]["Keyword(s)"])
        if len(effectKeywords.intersection(set("MagicAlchBeneficial"))) > 0:
            return 25
    return 0

def PoisonerPerk(effect, isPoison):
    if PoisonerRank == 1 and isPoison:
        effectName = effect["Effect Name"]
        effectKeywords = set(effectsDict[effectName]["Keyword(s)"])
        if len(effectKeywords.intersection(set("MagicAlchHarmful"))) > 0:
             return 25
    return 0

def PowerFactorSansAnyPerks():
    ingredientMult = fAlchemyIngredientInitMult = 4
    skillFactor = fAlchemySkillFactor = 1.5
    alchemySkill = Alchemy
    fortifyAlchemy = AlchemyMod #the sum of all active Fortify Alchemy effects
    power = ingredientMult * (1 + (skillFactor - 1) * alchemySkill / 100) * (1 + fortifyAlchemy / 100)
    return power

def PowerFactorSansKeywords():
    alchemistPerk = AlchemistPerk()
    power =  PowerFactorSansAnyPerks() * (1 + alchemistPerk / 100)
    return power

def PowerFactor(effect, isPoison): #effect is the subdictionary from the ingredientsDict
    physicianPerk = PhysicianPerk(effect)
    benefactorPerk = BenefactorPerk(effect, isPoison)
    poisonerPerk = PoisonerPerk(effect, isPoison)
    power = PowerFactorSansKeywords() * (1 + physicianPerk / 100) * (1 + benefactorPerk/100 + poisonerPerk / 100)
    return power

    '''
    alternative result, wrong:
    ingredientMult * skillFactor ^ (alchemySkill / 100) * (1 + fortifyAlchemy / 100) * (1 + alchemistPerk / 100) * (1 + physicianPerk / 100) * (1 + benefactorPerk / 100 + poisonerPerk / 100)
    '''

def value(ingredientsDictEffectEntry, powerFactor):#effect's subentry in the ingredientsDict
    currentEffect = ingredientsDictEffectEntry

    effectName = currentEffect["Effect Name"]
    magnitude = float(currentEffect["Magnitude"])
    
    if (effectName in NoMagnitudeList): magnitude = 0.0
    magnitudeFactor = 1.0
    if (effectName not in PowerAffectsDurationList): magnitudeFactor = powerFactor
    magnitude = round(magnitude * magnitudeFactor)

    duration = float(currentEffect["Duration"])
    if (effectName in NoDurationList or duration < 0): duration = 0.0
    durationFactor = 1.0
    if (effectName in PowerAffectsDurationList): durationFactor = powerFactor
    duration = round(duration * durationFactor)

    magnitudeFactor = 1.0
    if (magnitude > 0 ): magnitudeFactor = magnitude
    durationFactor = 1.0
    if (duration > 0 ): durationFactor = duration / 10
    
    basecost = float(effectsDict[effectName]["Cost"])
    
    return basecost * pow(magnitudeFactor * durationFactor, 1.1)
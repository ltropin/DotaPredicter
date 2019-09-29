from django.db import models


class ProPlayer(models.Model):
    id = models.BigIntegerField(primary_key=True)
    steam_id = models.BigIntegerField()
    name = models.CharField(max_length=500)
    avatar = models.ImageField(unique=True, default='avatars/none.png', upload_to='avatars')

    def __str__(self):
        return self.name



class Hero(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=500)
    # dotabuff_name = models.CharField(max_length=500)
    # picture = models.ImageField(unique=True, default='heroes/none.png', upload_to='heroes')

    def __str__(self):
        return self.name


class HeroDotaBuff(models.Model):
    name = models.CharField(max_length=500)
    short_name = models.CharField(max_length=500)
    picture = models.ImageField(unique=True, default='heroes/none.png', upload_to='heroes')

    def __str__(self):
        return self.name


class HeroData(models.Model):
    player = models.ForeignKey(ProPlayer, on_delete=models.CASCADE)
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    matches = models.IntegerField()
    # win_rate = models.FloatField()
    kills = models.FloatField()
    deaths = models.FloatField()
    assists = models.FloatField()
    GPM = models.FloatField()
    XPM = models.FloatField()

class CMatch(models.Model):
    match_id = models.BigIntegerField()
    player_id = models.BigIntegerField(default=-1)
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    is_pick = models.BooleanField()

class SimpleMatch(models.Model):
    match_id = models.BigIntegerField()
    player_id = models.BigIntegerField(default=-1)
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)

class MatchInfo(models.Model):
    match_id = models.BigIntegerField(primary_key=True)
    # player = models.ForeignKey(ProPlayer, on_delete=models.CASCADE)
    lobby_type = models.IntegerField()
    game_mode = models.IntegerField()

    def __str__(self):
        return self.match_id
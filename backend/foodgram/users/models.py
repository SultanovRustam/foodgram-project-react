from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Follow(models.Model):
    """Модель подписки пользователя на автора рецепта"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-id']

    def __str__(self):
        return f'{self.user}{self.author}'

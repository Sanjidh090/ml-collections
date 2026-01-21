[over here](https://www.kaggle.com/c/nfl-big-data-bowl-2020/discussion/120375#688496)
*Here is the discussion post link..
# nyanp · 22nd in this Competition · Posted 6 years ago
## What kind of effort did you make to make your script robust?
Max Jeblick, 3rd in the competition refered decorators....see discussion for better understanding.
```python
fails = []

def return_default_value_if_fails(default_value):

    def decorator(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                fails.append((func, (args, kwargs), e))
                return default_value
        return inner

    return decorator
```
> example usage
```python
....
    def _parse_player_height(self):

        @return_default_value_if_fails(default_value=75)
        def parse(x):
            return 12 * int(x.split('-')[0]) + int(x.split('-')[1])
        return self.df['PlayerHeight'].apply(parse)
....
```

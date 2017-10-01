
company = 'ytml'
"""
`company` variable will be modified when user logged in, and reset to 'ytml'
when logged out, is accessible to all other modules across the application
"""

ratio_list = {}
"""
`ratio_list` is in a form like {[Group, SubGroup, Variable]: 0.956}, will store
top 5 best match ratio result for fuzzy search
"""

minimum_ratio = 0
"""
`minimum_ratio` records the current minimal ratio. A coming ratio will be
dropped if it is smaller than it, and it will be appended to ratio_list if it
is larger than it, in this case the minimum_ratio will be updated according to
current ratio_list
"""

pattern = ''
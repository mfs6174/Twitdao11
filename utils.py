
_urlsafe_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.'
_urlsafe_chars_num=len(_urlsafe_chars)

def tweet_id_encode(n):
    tl, n = [], long(n)
    while(n>0):
        m, n = n%_urlsafe_chars_num, n//_urlsafe_chars_num
        tl.insert(0,_urlsafe_chars[int(m)])
    return ''.join(tl)

def tweet_id_decode(t):
    t=str(t)
    n,i=0,len(t)-1
    for c in t:
        if c not in _urlsafe_chars: return 0
        n+=(_urlsafe_chars.index(c)*pow(_urlsafe_chars_num, i))
        i-=1
    return n

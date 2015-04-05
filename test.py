# coding: utf-8
import sys
import os
stdin = sys.stdin
stdout = sys.stdout
sys.path.insert(0,'lib')
reload(sys)
sys.setdefaultencoding('utf-8')
sys.stdin = stdin
sys.stdout = stdout
#sys.path.append(os.pardir)
sys.path.append(os.pardir + '/lib/')
#os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from BeautifulSoup import BeautifulSoup as BeautifulSoup

test = u'''
<dl class="column-related inline-list"><dt>関連タグ</dt><dd><ul class="tags"><li class="tag"><a href="tags.php?tag=%E3%82%B1%E3%83%A2%E3%83%8E" class="portal">c</a><a href="/search.php?s_mode=s_tag_full&amp;word=%E3%82%B1%E3%83%A2%E3%83%8E" class="text">ケモノ</a></li><li class="tag"><a href="tags.php?tag=%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3" class="portal">c</a><a href="/search.php?s_mode=s_tag_full&amp;word=%E3%83%9D%E3%82%B1%E3%83%A2%E3%83%B3" class="text">ポケモン</a></li><li class="tag"><a href="tags.php?tag=%E3%82%B1%E3%83%A2%E3%83%9B%E3%83%A2" class="portal">c</a><a href="/search.php?s_mode=s_tag_full&amp;word=%E3%82%B1%E3%83%A2%E3%83%9B%E3%83%A2" class="text">ケモホモ</a></li><li class="tag"><a href="tags.php?tag=%E6%BC%AB%E7%94%BB" class="portal">c</a><a href="/search.php?s_mode=s_tag_full&amp;word=%E6%BC%AB%E7%94%BB" class="text">漫画</a></li><li class="tag"><a href="tags.php?tag=%E3%83%A1%E3%82%B9%E3%82%B1%E3%83%A2" class="portal">c</a><a href="/search.php?s_mode=s_tag_full&amp;word=%E3%83%A1%E3%82%B9%E3%82%B1%E3%83%A2" class="text">メスケモ</a></li><li class="tag"><a href="tags.php?tag=%E3%82%B1%E3%83%A2%E3%82%B7%E3%83%A7%E3%82%BF" class="portal">c</a><a href="/search.php?s_mode=s_tag_full&amp;word=%E3%82%B1%E3%83%A2%E3%82%B7%E3%83%A7%E3%82%BF" class="text">ケモショタ</a></li><li class="tag"><a href="tags.php?tag=%E3%82%AA%E3%82%B9%E3%82%B1%E3%83%A2" class="portal">c</a><a href="/search.php?s_mode=s_tag_full&amp;word=%E3%82%AA%E3%82%B9%E3%82%B1%E3%83%A2" class="text">オスケモ</a></li><li class="tag"><a href="tags.php?tag=%E3%83%AC%E3%83%91%E3%83%AB%E3%83%80%E3%82%B9" class="portal">c</a><a href="/search.php?s_mode=s_tag_full&amp;word=%E3%83%AC%E3%83%91%E3%83%AB%E3%83%80%E3%82%B9" class="text">レパルダス</a></li></ul></dd></dl>
'''
def main():
    soup = BeautifulSoup(test)
    for tag in soup.findAll('a', {'class':'text'}):
      relatedtag = str(tag.string)
      print relatedtag

main()

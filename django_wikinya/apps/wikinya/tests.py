"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import WikiPage, WikiImage, WikiAttachement
from django.contrib.auth.models import User

from syntax import LinkTag
import factory
from model_mommy import mommy


class UserFactory(factory.Factory):
    FACTORY_FOR = User

class WikiPageFactory(factory.Factory):
    FACTORY_FOR = WikiPage
    author = factory.LazyAttribute(lambda a: UserFactory())

class SimpleTest(TestCase):
    def test_basic_addition(self):
        wp = mommy.make_one(WikiPage)
        assert wp.id == 1
        assert wp.author.id == 1


class LinkTagTest(TestCase):
    def test_generic(self):
        link = LinkTag('test', attrs={'href':'http://ya.ru'})
        link.parse()
        assert u'<a href="http://ya.ru">test</a>' == link.render()

    def test_interpage(self):
        wiki_page = mommy.make_one(WikiPage, title='test')
        link = LinkTag('test', attrs={'href':'page:test'})
        link.parse()
        assert u'<a href="/wiki/test" class="wiki_link">test</a>' == link.render(), link.render()

        link = LinkTag('test', attrs={'href':'page:test/test2'})
        link.parse()
        assert u'<a href="/wiki/test/test2" class="wiki_link no_wiki_page">test</a>' == link.render(), link.render()

    def test_link_image(self):
        wiki_image = mommy.make_one(WikiImage, title='test.jpeg', image='test.jpeg')
        link = LinkTag('test', attrs={'href':'image:test/test.jpeg'})
        link.parse()
        assert u'<a href="/media/test.jpeg" class="wiki_link">test</a>' == link.render(), link.render()

    def test_link_attach(self):
        wiki_image = mommy.make_one(WikiAttachement, title='test.zip', attach='test.zip')
        link = LinkTag('test', attrs={'href':'attach:test/test.zip'})
        link.parse()
        assert u'<a href="/media/test.zip" class="wiki_link">test</a>' == link.render(), link.render()

class WikiPageTest(TestCase):
    def test_get_page(self):
        page = mommy.make_one(WikiPage, title='p1')
        page2 = mommy.make_one(WikiPage, title='p2', parent_page=page)

        assert WikiPage.get_object_by_path('/'.join([page.title])) != None
        assert WikiPage.get_object_by_path('/'.join([page.title, page2.title])) != None

    def test_make_path(self):
        page = mommy.make_one(WikiPage, title='p1')
        page2 = mommy.make_one(WikiPage, title='p2', parent_page=page)
        pages = WikiPage.make_path('p1/p2/p3')
        assert page.id == pages[0].id
        assert page2.id == pages[1].id
        assert len(pages) == 2


    def test_make_path_one_parent(self):
        page = mommy.make_one(WikiPage, title='p1')
        pages = WikiPage.make_path('p1/p2')
        assert page.id == pages[0].id
        assert len(pages) == 1

    def test_make_path_one(self):
        page = mommy.make_one(WikiPage, title='p1')

        pages = WikiPage.make_path('p1')
        assert len(pages) == 0
        assert WikiPage.objects.count() == 1





class SimpleSyntaxTest(TestCase):
    def test_generic(self):
        from syntax import creole2html
        wiki_text = u'''
        = Top-level heading (1)
== This a test for creole 0.1 (2)
=== This is a Subheading (3)
==== Subsub (4)
===== Subsubsub (5)

The ending equal signs should not be displayed:

= Top-level heading (1) =
== This a test for creole 0.1 (2) ==
=== This is a Subheading (3) ===
==== Subsub (4) ====
===== Subsubsub (5) =====


You can make things **bold** or //italic// or **//both//** or //**both**//.

Character formatting extends across line breaks: **bold,
this is still bold. This line deliberately does not end in star-star.

Not bold. Character formatting does not cross paragraph boundaries.

You can use [[internal links]] or [[http://www.wikicreole.org|external links]],
give the link a [[internal links|different]] name.

Here's another sentence: This wisdom is taken from [[Ward Cunningham's]]
[[http://www.c2.com/doc/wikisym/WikiSym2006.pdf|Presentation at the Wikisym 06]].

Here's a external link without a description: [[http://www.wikicreole.org]]

Be careful that italic links are rendered properly:  //[[http://my.book.example/|My Book Title]]//

Free links without braces should be rendered as well, like http://www.wikicreole.org/ and http://www.wikicreole.org/users/~example.

Creole1.0 specifies that http://bar and ftp://bar should not render italic,
something like foo://bar should render as italic.

You can use this to draw a line to separate the page:
----

You can use lists, start it at the first column for now, please...

unnumbered lists are like
* item a
* item b
* **bold item c**

blank space is also permitted before lists like:
  *   item a
 * item b
* item c
 ** item c.a

or you can number them
# [[item 1]]
# item 2
# // italic item 3 //
    ## item 3.1
  ## item 3.2

up to five levels
* 1
** 2
*** 3
**** 4
***** 5

* You can have
multiline list items
* this is a second multiline
list item

You can use nowiki syntax if you would like do stuff like this:

{{{
Guitar Chord C:

||---|---|---|
||-0-|---|---|
||---|---|---|
||---|-0-|---|
||---|---|-0-|
||---|---|---|
}}}

You can also use it inline nowiki {{{ in a sentence }}} like this.

= Escapes =
Normal Link: http://wikicreole.org/ - now same link, but escaped: ~http://wikicreole.org/

Normal asterisks: ~**not bold~**

a tilde alone: ~

a tilde escapes itself: ~~xxx

=== Creole 0.2 ===

This should be a flower with the ALT text "this is a flower" if your wiki supports ALT text on images:

{{Red-Flower.jpg|here is a red flower}}

=== Creole 0.4 ===

Tables are done like this:

|=header col1|=header col2|
|col1|col2|
|you         |can         |
|also        |align\\ it. |

You can format an address by simply forcing linebreaks:

My contact dates:\\
Pone: xyz\\
Fax: +45\\
Mobile: abc

=== Creole 0.5 ===

|= Header title               |= Another header title     |
| {{{ //not italic text// }}} | {{{ **not bold text** }}} |
| //italic text//             | **  bold text **          |

=== Creole 1.0 ===

If interwiki links are setup in your wiki, this links to the WikiCreole page about Creole 1.0 test cases: [[WikiCreole:Creole1.0TestCases]].
        '''
        html_text = '''<p>        = Top-level heading (1)</p>
<h2>This a test for creole 0.1 (2)</h2>
<h3>This is a Subheading (3)</h3>
<h4>Subsub (4)</h4>
<h5>Subsubsub (5)</h5>

<p>The ending equal signs should not be displayed:</p>

<h1>Top-level heading (1)</h1>
<h2>This a test for creole 0.1 (2)</h2>
<h3>This is a Subheading (3)</h3>
<h4>Subsub (4)</h4>
<h5>Subsubsub (5)</h5>

<p>You can make things <strong>bold</strong> or <i>italic</i> or <strong><i>both</i></strong> or <i><strong>both</strong></i>.</p>

<p>Character formatting extends across line breaks: **bold,<br />
this is still bold. This line deliberately does not end in star-star.</p>

<p>Not bold. Character formatting does not cross paragraph boundaries.</p>

<p>You can use <a href="internal links">internal links</a> or <a href="http://www.wikicreole.org">external links</a>,<br />
give the link a <a href="internal links">different</a> name.</p>

<p>Here's another sentence: This wisdom is taken from <a href="Ward Cunningham's">Ward Cunningham's</a><br />
<a href="http://www.c2.com/doc/wikisym/WikiSym2006.pdf">Presentation at the Wikisym 06</a>.</p>

<p>Here's a external link without a description: <a href="http://www.wikicreole.org">http://www.wikicreole.org</a></p>

<p>Be careful that italic links are rendered properly:  <i><a href="http://my.book.example/">My Book Title</a></i></p>

<p>Free links without braces should be rendered as well, like <a href="http://www.wikicreole.org/">http://www.wikicreole.org/</a> and <a href="http://www.wikicreole.org/users/~example">http://www.wikicreole.org/users/~example</a>.</p>

<p>Creole1.0 specifies that <a href="http://bar">http://bar</a> and <a href="ftp://bar">ftp://bar</a> should not render italic,<br />
something like foo://bar should render as italic.</p>

<p>You can use this to draw a line to separate the page:</p>
<hr />

<p>You can use lists, start it at the first column for now, please...</p>

<p>unnumbered lists are like</p>
<ul>
	<li>item a</li>
	<li>item b</li>
	<li><strong>bold item c</strong></li>
</ul>
<p>blank space is also permitted before lists like:</p>
<ul>
	<li>item a</li>
	<li>item b</li>
	<li>item c
	<ul>
		<li>item c.a</li>
	</ul></li>
</ul>
<p>or you can number them</p>
<ol>
	<li><a href="item 1">item 1</a></li>
	<li>item 2</li>
	<li><i> italic item 3 </i>
	<ol>
		<li>item 3.1</li>
		<li>item 3.2</li>
	</ol></li>
</ol>
<p>up to five levels</p>
<ul>
	<li>1
	<ul>
		<li>2
		<ul>
			<li>3
			<ul>
				<li>4
				<ul>
					<li>5</li>
				</ul></li>
			</ul></li>
		</ul></li>
	</ul></li>
</ul>
<ul>
	<li>You can havemultiline list items</li>
	<li>this is a second multilinelist item</li>
</ul>
<p>You can use nowiki syntax if you would like do stuff like this:</p>

<pre>
Guitar Chord C:

||---|---|---|
||-0-|---|---|
||---|---|---|
||---|-0-|---|
||---|---|-0-|
||---|---|---|
</pre>

<p>You can also use it inline nowiki <tt> in a sentence </tt> like this.</p>

<h1>Escapes</h1>
<p>Normal Link: <a href="http://wikicreole.org/">http://wikicreole.org/</a> - now same link, but escaped: http://wikicreole.org/</p>

<p>Normal asterisks: **not bold**</p>

<p>a tilde alone: ~</p>

<p>a tilde escapes itself: ~xxx</p>

<h3>Creole 0.2</h3>

<p>This should be a flower with the ALT text "this is a flower" if your wiki supports ALT text on images:</p>

<p><img src="Red-Flower.jpg" alt="here is a red flower" title="here is a red flower"/></p>

<h3>Creole 0.4</h3>

<p>Tables are done like this:</p>

<table>
<tr>
	<th>header col1</th>
	<th>header col2</th>
</tr>
<tr>
	<td>col1</td>
	<td>col2</td>
</tr>
<tr>
	<td>you</td>
	<td>can</td>
</tr>
<tr>
	<td>also</td>
	<td>align\ it.</td>
</tr>
</table>
<p>You can format an address by simply forcing linebreaks:</p>

<p>My contact dates:\Pone: xyz\Fax: +45\Mobile: abc</p>

<h3>Creole 0.5</h3>

<table>
<tr>
	<th>Header title</th>
	<th>Another header title</th>
</tr>
<tr>
	<td><tt> //not italic text// </tt></td>
	<td><tt> **not bold text** </tt></td>
</tr>
<tr>
	<td><i>italic text</i></td>
	<td><strong>  bold text </strong></td>
</tr>
</table>
<h3>Creole 1.0</h3>

<p>If interwiki links are setup in your wiki, this links to the WikiCreole page about Creole 1.0 test cases: <a href="WikiCreole:Creole1.0TestCases">WikiCreole:Creole1.0TestCases</a>.</p>'''
        html = creole2html(wiki_text)
        assert html == html_text

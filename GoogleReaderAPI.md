**Note** : This document is totally unofficial. You should **not** rely on anything on this document is you **need** an exact information.
Google Reader API has not officially been released. This document has been made mainly by reverse engeneering the protocol.

# Requierements #

Google Reader API require :
  * http client
  * GET and POST support
  * Cookie support
  * https client

https is only required for identification with Google to get the string called **SID**. You can rely on an external tool to connect with https and give you SID. If you do, https won't be required.

Cookie support is only required to pass to all pages the current **SID**, proof of identification. If are able to change add lines in headers, cookie support is not required anymore.

Google Reader API may require :
  * http client
  * GET and POST support
  * external tool to get **SID** (using https)
  * putting **SID** into header

# Glossary #

  * **SID** : Session ID. SID is generated each time you login to Google (any service). The SID is valid until you logout.
  * **user ID** : a 20 digits string used by google reader to identify a user. You don't really need to know it. You can always do things a way that user ID is not needed. Usually, when you need that information, just replace it by **-** and the user ID for current logged user will be used. The user ID never change for a user.
  * **token** : A token is a special 57 chars string that is used like a session identification, but that expire rather quickly. You usaully need a token for direct api calls that change informations. The token is valid for few minutes/hours. If API call fail (doesn't return OK), you just have to get antoher token.
  * **client ID** : A string that identify the client used. I suppose it's for logging/stat purpose, or perhaps to make some adjustement for some clients, but I doubt so. old GoogleReader interface use `'lens'`, new one use `'scroll'`. The writer of this document use `'contact:`_name_`-at-`_host_`'` for interactive test, and use string like `'pyrfeed/0.5.0'` for the software _pyrfeed_ in version _0.5.0_ (like classical identification strings for unix softwares).
  * **item**/**entry** : Sometimes called _item_, sometimes called _entry_, the item is the base element of a feed. An item usally contain a text, a title and a link, but can contain other properties. An RSS/Atom aggregator aggregates items. (Note: _item_ is the RSS term, while _entry_ is the Atom term).

# Identification #

**Note** : According to Mihai Parparita in Google Reader Support Group ( http://groups.google.com/group/Google-Labs-Reader/browse_frm/thread/73a0aed708bcd005 ), "Authentication is one of the reason why the API hasn't been released yet". You should expect big changes before Google Reader release official API.

To login, you need to post with https on https://www.google.com/accounts/ClientLogin with the following POST parameters :

| **POST parameter name** | **POST parameter value** |
|:------------------------|:-------------------------|
| service                 | `'reader'` (!)           |
| Email                   | _your login_             |
| Passwd                  | _your password_          |
| source                  | _your client string identification_ (!) |
| continue                | `'http://www.google.com/'` (!) |

> Of course, _your login_ and _your password_ are login and password you usually use to identify interactively to Google.

(!) : Those parameters are said to be optional ( http://code.google.com/p/pyrfeed/issues/detail?id=10 ). I didn't really tested. It's just how "browsers" identifies themselfs. Note that I consider _source_ and _service_ as a being  informative parameters for google, so I feel like I **need** to provide them, event if they are not required. Note that I have no idea about what Google or the Google Reader team really think about that. Perhaps they prefer "nothing but a crafted information", or perhaps they don't care. Who knows...

> There is no official rule _your client string identification_, see **client ID** in glossary for more informations.

The POST action will return you a text file, containing lines of the form :

> _key_=_value_

You need to extract the _value_ for the _key_ named `SID`

You then have to add yourself a cookie (well, it look like Google doesn't add it itself) with the following properties :
| name | `SID` |
|:-----|:------|
| domain | `.google.com` |
| path | `/`   |
| expires | `1600000000` |

If you don't have a http client API that support cookies, you can just add header lines that simulate this cookie in all other requests. This should be the only thing for which cookies are really needed.

# The three layers for feed aggregators #

When you're writting a feed aggregator, you need to write three different layers :
  * **Layer 1** : The layer that parse feeds. It's not the easiest job. "But, it's just xml, it should be easy". It's not. It's just xml. It's just 10 differents and incompatible xml formats (9 RSS formats according to Mark Pilgrim and 1 Atom format). You also perhaps need to understand all non standard feeds that mix some features from differents standards.
  * **Layer 2** : The database layer. Once you've parsed your feed, you need to store it in a database, and and interesting things like "items read", etc.
  * **Layer 3** : The user interface.

Google Reader offer in fact acces to **layer 1** only, or **layer 1+2** or **layer 1+2+3**.

You can have acces to **layer 1** only. Feeds are parsed by Google Reader, and Google Reader give you access to a new Atom feed that contains same data as the original feed, but always with the same output format : Atom.

You can have acces to **layer 1+2**. This documents purpose is about how to acces to **layer 1+2** from Google Reader in order to create your own **layer 3**.

Of course, you have access to **layer 1+2+3** because it's Google Reader's main product.

# Url scheme #

Except for identification process, all Google Reader url ressources start with `http://www.google.com/reader/`. We'll explain here direct subspaces of thoses urls.

| **URL prefix** | **Will be refered as, in  this document** | **Description** |
|:---------------|:------------------------------------------|:----------------|
| `http://www.google.com/reader/atom/` | _/atom/_                                  | All urls starting by this prefix return atom feeds. It's the (only?) way to acces to feed contents. This is the way to access **layer 1** and **layer 1+2**. |
| `http://www.google.com/reader/api/0/` | _/api/0/_                                 | This is the main API entry point. It's used for items/feeds modifications, like adding a _Star_, deleting a tag, etc. For those modification services, it return either `"OK"` or `""`. It's also used to consult some setting lists like list of feeds, list of tags, list of unread counts by feeds/tags, etc. For those read services, it returns an _"object"_ that can be either _[json](http://json.org/)_ or _xml that look like json_. This is a **layer 2** only zone. |
| `http://www.google.com/reader/view/` | _/view/_                                  | All AJAX interface is done by /view/ urls. AJAX code use _/atom/_ and _/api/0/_ as sublayers to do the job. This is the way to access **layer 3**. |
| `http://www.google.com/reader/shared/` | _/shared/_                                | All shared pages use this prefix. You obviously don't need authentification to use those pages. |
| `http://www.google.com/reader/settings/` | _/settings/_                              | The AJAX application to configure all settings. Mainly manipulate informations from _/api/0/_. This part of **layer 3**. |

## Atom set of items ##

_this section is about urls starting by `http://www.google.com/reader/atom/`_

The Google Reader database contains a huge number of items. Some of them are in your _reading list_ (understand, they are accessible in Google Reader for your account in "_All items_" section, and in your feeds/tags).

The only way to get information related to an item is to "query an atom set of items" that contain this item.

All items are or were included in feeds. One way to query items is to query the original feed.

Item are also associated to categories. tags/labels are categories, but also the "read" state is also a category.

Antoher way to query items is to query all items that are associated to a category.

| **Set of items suffix** | | | | **Description** |
|:------------------------|:|:|:|:----------------|
| `feed/`                 | _url of a feed_ | | | The url to query a specific feed. It's Google Reader way to access to **layer 1** only. **Note** : This service is not related to an account and can be access without registration. |
| `user/`                 | _user ID_`/` | `label/` | _label name_ | This is the suffix to access to all items with a specific label |
| `user/`                 | _user ID_`/` | `state/com.google/` | _state_ | This is the suffix to access to all items with a specific state like **`read`**, **`starred`**, etc. |

You can use `-` as your **user ID**, it will use the **user ID** for your currently identified account.

| **State name** | **State meaning** |
|:---------------|:------------------|
| `read`         | A read item will have the state _read_ |
| `kept-unread`  | Once you've clicked on "keep unread", an item will have the state _kept-unread_ |
| `fresh`        | When a new item of one of your feeds arrive, it's labeled as _fresh_. When (_need to find what remove fresh label_), the fresh label disappear. |
| `starred`      | When your mark an item with a star, you set it's _starred_ state |
| `broadcast`    | When your mark an item as being public, you set it's _broadcast_ state |
| `reading-list` | All you items are flagged with the _reading-list_ state. To see all your items, just ask for items in the state `reading-list` |
| `tracking-body-link-used` | Set if you ever clicked on a link in the description of the item. |
| `tracking-emailed` | Set if you ever emailed the item to someone. |
| `tracking-item-link-used` | Set if you ever clicked on a link in the description of the item. |
| `tracking-kept-unread` | Set if you ever mark your read item as unread. |

If you need to query a set of items in an atom format, just query `http://www.google.com/reader/atom/` followed by the set of items suffix.

For exemple, if you want to acces to Google Reader's rewritting of the feed http://xkcd.com/rss.xml , you can query http://www.google.com/reader/atom/feed/http://xkcd.com/rss.xml . This can be done whether you are identified or not.
If you want to query all your last read items, you can query http://www.google.com/reader/atom/user/-/state/com.google/read .

Each atom set contains by default 20 items. You can change that, and other behaviour by adding parameters to the query.

| **GET parameter name** | **python Google Reader API name** | **parameter value** |
|:-----------------------|:----------------------------------|:--------------------|
| `n`                    | _count_                           | Number of items returns in a set of items (default 20) |
| `client`               | _client_                          | The default client name (see _client_ in glossary) |
| `r`                    | _order_                           | By default, items starts now, and go back time. You can change that by specifying this key to the value `o` (default value is `d`) |
| `ot`                   | _start\_time_                     | The time (unix time, number of seconds from January 1st, 1970 00:00 UTC) from which to start to get items. Only works for order r=o mode. If the time is older than one month ago, one month ago will be used instead. |
| `ck`                   | _timestamp_                       | current time stamp, probably used as a quick hack to be sure that cache won't be triggered. |
| `xt`                   | _exclude\_target_                 | another set of items suffix, to be excluded from the query. For exemple, you can query all items from a feed that are not flagged as read. This value start with `feed/` or  `user/`, not with `!http://` or `www` |
| `c`                    | _continuation_                    | a string used for _continuation_ process. Each feed return not all items, but only a certain number of items. You'll find in the atom feed (under the name `gr:continuation`) a string called continuation. Just add that string as argument for this parameter, and you'll retrieve next items. |

**Note** : _continuation_ has no meaning, it's just a string to help you find next items. You should not rely on its value to do anything else than that (even if this document will explain how that continuation is generated).

**Exemple** :
> All the 17 first items items from xkcd.com main feed that are not read can be found on the url : http://www.google.com/reader/atom/feed/http://xkcd.com/rss.xml?n=17&ck=1169900000&xt=user/-/state/com.google/read

## API ##

_this section is about urls starting by `http://www.google.com/reader/api/0/`_

There are two knids of API commands:
  * edit commands
  * list commands

The number 0 is probably the API version number. Using that number, it will allow Google Reader to change API while stile maintaining an old API for quite some time.

### Edit API ###

To edit anything in the Google Reader database, you need a token (see glossary).
To get a token, just go to http://www.google.com/reader/api/0/token . This url will return a string containing 57 chars. It's the token.

The token url takes optional GET arguments:

| **GET parameter name** | **python Google Reader API name** | **parameter value** |
|:-----------------------|:----------------------------------|:--------------------|
| `ck`                   | _timestamp_                       | current time stamp, probably used as a quick hack to be sure that cache won't be triggered. |
| `client`               | _client_                          | The default client name (see _client_ in glossary) |

All edit commands use `POST` to retrieve information (note that GET won't work) but they also take a `GET` argument.

| **GET parameter name** | **python Google Reader API name** | **parameter value** |
|:-----------------------|:----------------------------------|:--------------------|
| `client`               | _client_                          | The default client name (see _client_ in glossary) |

All edit commands will return either an empty string if failled, either the string "`OK`". If failed, your token has perhaps expires. You can just try to get a new token. If it still doesn't return OK, it's a failure.

Table of POST aguments for the `subscription/edit` edit call.

| **API call function** | **POST parameter name** | **python Google Reader API name** | **parameter value** |
|:----------------------|:------------------------|:----------------------------------|:--------------------|
|  **`subscription/edit`** | | | |
|                       | `s`                     | _feed_                            | The subscription feed name, in the form `feed/`_..._ |
|                       | `t`                     | _title_                           | The subscription title, used when adding a new subscription or when changing a subscription name |
|                       | `a`                     | _add_                             | A label to add (a label on a subscription is called a folder) in the form `user/`_..._ |
|                       | `r`                     | _remove_                          | A label to remove (a label on a subscription is called a folder) in the form `user/`_..._ |
|                       | `ac`                    | _action_                          | The actions to do. Know values are `edit` (to add/remove label/forlder to a feed), 'subscribe', 'unsubscribe' |
|                       | `token`                 | _token_                           | The mandatory up to date token |
|  **`tag/edit`**       | | | |
|                       | `s`                     | _feed_                            | The tag/folder name seen as a feed |
|                       | `pub`                   | _public_                          | A boolean string `true` or `false`. When `true`, the tag/folder will become public. When `false`, the tag/folder will stop being public. |
|                       | `token`                 | _token_                           | The mandatory up to date token |
|  **`edit-tag`**       | | | |
|                       | `i`                     | _entry_                           | The item/entry to edit, in the form `tag:google.com,2005:reader/item/`_..._ ( it's the xml id of the `entry` tag of the atom feed) |
|                       | `a`                     | _add_                             | A label/state to add (a label on an item/entry is called a tag) in the form `user/`_..._ |
|                       | `r`                     | _remove_                          | A label/state to remove (a label on an item/entry is called a tag) in the form `user/`_..._|
|                       | `ac`                    | _action_                          | The actions to do. Know value is `edit` (to add/remove label/forlder to a feed) |
|                       | `token`                 | _token_                           | The mandatory up to date token |
|  **`disable-tag`**    | | | |
|                       | `s`                     | _feed_                            | The tag/folder name seen as a feed |
|                       | `ac`                    | _action_                          | The actions to do. Know value is `disable-tags` (to remove a tag/folder) |
|                       | `token`                 | _token_                           | The mandatory up to date token |

Exemples :
> To subscribe a new feed (for exemple http://xkcd.com/rss.xml), you can call:

> http://www.google.com/reader/api/0/subscription/edit?client=contact:myname-at-gmail

> with POST arguments : `s=http://xkcd.com/rss.xml&ac=subscribe&token=`_here-put-a-valid-token_

> To add that feed in a folder (for exemple "comics"), you can call:

> http://www.google.com/reader/api/0/subscription/edit?client=contact:myname-at-gmail

> with POST arguments : `s=http://xkcd.com/rss.xml&ac=edit&a=user/-/label/comics&token=`_here-put-a-valid-token_

Open questions that needs to be fixed :
  * Are `tag/edit` and `edit-tag` just aliases ?
  * Why does removing a tag/folder doesn't take an action while every other calls take actions ?
  * Why is there several urls, it seems redundant with the action parameter ?

### List API ###

All those calls can be used with GET requests.

| **API call function** | **GET parameter name** | **python Google Reader API name** | **parameter value**/**API call description** |
|:----------------------|:-----------------------|:----------------------------------|:---------------------------------------------|
| **`tag/list`**        | | | Get the tag list and shared status for each tag. |
|                       | `output`               | _output_                          | The format of the returned output. may be 'json' or 'xml' |
|                       | `ck`                   | _timestamp_                       | current time stamp, probably used as a quick hack to be sure that cache won't be triggered. |
|                       | `client`               | _client_                          | The default client name (see _client_ in glossary) |
| **`subscription/list`** | | | Get the subscription list and shared status for each tag. |
|                       | `output`               | _output_                          | The format of the returned output. may be 'json' or 'xml' |
|                       | `ck`                   | _timestamp_                       | current time stamp, probably used as a quick hack to be sure that cache won't be triggered. |
|                       | `client`               | _client_                          | The default client name (see _client_ in glossary) |
| **`preference/list`** | | | Get the preference list (configuration of the account for GoogleReader). |
|                       | `output`               | _output_                          | The format of the returned output. may be 'json' or 'xml' |
|                       | `ck`                   | _timestamp_                       | current time stamp, probably used as a quick hack to be sure that cache won't be triggered. |
|                       | `client`               | _client_                          | The default client name (see _client_ in glossary) |
| **`unread-count`**    | | | Get all the information about where are located (in term of subscriptions and tags/folders) the unread items. |
|                       | `all`                  | _all_                             | 'true' if whole subscriptions/tags are required. (**TODO**: _Needs to check other values_)  |
|                       | `output`               | _output_                          | The format of the returned output. may be 'json' or 'xml' |
|                       | `ck`                   | _timestamp_                       | current time stamp, probably used as a quick hack to be sure that cache won't be triggered. |
|                       | `client`               | _client_                          | The default client name (see _client_ in glossary) |

## Viewer ##

_this section is about urls starting by `http://www.google.com/reader/view/`_

All url starting by http://www.google.com/reader/view/ are html pages that use AJAX code to show atom feeds found from http://www.google.com/reader/atom/.

You can append to the base url any _set of items suffix_ to view only that set of items. Note however that GET parameters are not valid (in fact are ignored) for those urls.

You can browse directly all your items labeled "important" by going to http://www.google.com/reader/view/user/-/label/important

You can browse directly all items from xkcd main feed by going to http://www.google.com/reader/view/feed/http://xkcd.com/rss.xml even if you didn't subscribed to it (in which case there will be a button "Subscribe" on the top of the screen). Note however that if you're not identified, you'll browse the feed using the old interface (lens) and not the new on (scroll).

## Misc ##

_TODO: Text needs to be written_
_TODO: mainly /share/_

# References #

  * http://www.niallkennedy.com/blog/archives/2005/12/google_reader_a.html : First document being consided as an unofficial Google Reader API.
  * http://www.xml.com/pub/a/2002/12/18/dive-into-xml.html : Mark Pilgrim explaining the mess with all RSS formats

![http://pyrfeed.yi.org/image.png](http://pyrfeed.yi.org/image.png)



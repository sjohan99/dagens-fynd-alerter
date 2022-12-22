# SweClockers Dagens Fynd Discord Bot

Discord bot which scrapes deals suggested by users on <a href="https://www.sweclockers.com/">sweclockers.com</a>.

Get notified whenever a new deal is posted to the forum or subscribe to specific keyword if you're only interested in a some products.

Supports the following commands:
<ul>
  <li><code>df set-channel CHANNEL_NAME</code> to set the channel the bot should post to</li>
  <li><code>df remove-channel</code> removes current posting channel</li>
  <li><code>df sub</code> to get notified when any new deal is posted</li>
  <li><code>df unsub</code> to stop getting notified when any new deal is posted</li>
  <li><code>df sub-kw KEYWORD</code> subscribe to a given keyword such as RTX or i7 to get notified when a new deal containing that keyword is posted</li>
  <li><code>df unsub-kw KEYWORD</code> unsubscribe from the given keyword</li>
  <li><code>df my-kws</code> to see which keywords you're currently subscribed to</li>

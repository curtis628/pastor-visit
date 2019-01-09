from django.core.management.base import BaseCommand

from homevisit.models import Faq


class Command(BaseCommand):
    help = "creates initial FAQ content"

    def handle(self, *args, **options):
        cancel = Faq(short_name="cancel")
        cancel.question = "What if I need to cancel my scheduled meeting?"
        cancel.answer = (
            "No problem! Just let me know using the <a href='/contact'>Contact Us</a> "
            "page. This will email me and I'll take care of marking your meeting slot as"
            "available for other folks."
        )
        cancel.save()
        self.stdout.write(self.style.SUCCESS("Successfully created 'cancel' FAQ"))

        none_avail = Faq(short_name="no-availability")
        none_avail.question = (
            "What if there are no available meeting times that work for me?"
        )
        none_avail.answer = (
            "<p>Please understand that it may take us quite a while to get to your house "
            'because we want to model maintaining "balance" in our lives for each of '
            "you so that we will have margins in our lives as opposed to stress! We "
            'believe the "slow and steady wins the race"!!</p>'
            "<p>Please check back later, or you can <a href='/contact'>contact us</a> so "
            "we can let you know when more availability comes up!</p>"
        )
        none_avail.save()
        self.stdout.write(
            self.style.SUCCESS("Successfully created 'no-availability' FAQ")
        )

        about = Faq(short_name="about")
        about.question = "About"
        about.answer = """
<p>Dear Firm Family,</p>
<p>
You folks are truly a HUGE blessing to Lindy and I!  We love you and love your:
<ul>
  <li>Love for one another
  <li>Commitment to accept one another from all ages and stages
  <li>Desire to develop a faith that is real
  <li>Desire to develop friends that are true
  <li>Desire to think Biblically, live distinctively and love correctly
  <li>Desire to impact our world for Christ
  <li>Your generosity towards the needs of our church, missionaries all over the world and
    this community
  <li>Your sense of humor and willingness to laugh "with us" as opposed to "at us"
</ul>
</p>
<p>
But here is a disappointment of God blessing us with more and more folks:  We feel like we
haven't gotten to know you all as well as we would love to.  With close to 300 folks in
the gym each Sunday morning it has become more difficult to even know everyone's names
and their children's names. I like to "dream a dream and build a team" myself so am
about to share that dream with you and how you are a part of the team!
</p>
<p>
Before I share my dream with you, let me tell you that my dream was inspired by the
original dream of Jason Poling at Cornerstone Church in Yuba City!  I forewarned him that
I LOVED his idea and was hijacking it to Chico!!  He shared with his people that the
dream was a little "weird" to us today, but very common to pastors and congregations 100
years ago!!  I like old!
</p>
<p>
Now for the dream: <u>Lindy and I want to come to your home and hang out with you!</u>
So let me tell you why we want to do this.  I want to make sure this adventure is both
safe and predictable so you will have no worries or apprehension about us coming over!!
</p>

<h4 class="text-dark">Why do we want to come to your house?</h4>
<p>
<ul>
  <li>We would love to get some time with you in a very small "circle" as we all know it
  is very difficult to get to know people in "rows".
  <li>Coming to where you live helps us learn more about you, your family, hobbies,
  personalities, pets you love, etc.
  <li>Knowing just those few things about you will us better pray for you and serve you
  in the days ahead.
</ul>
</p>

<h4 class="text-dark">Clarification About Expectations</h4>
<p>
PLEASE don’t let the size or state of your house be an issue.  I hope you know there will
be NO judgements passed about how you live.  Pastor Jason says to him "an immaculate
house demonstrates just as many personality quirks as a messy house!"  Truth is, we are
all a bit quirky in our own ways to let's just admit it and accept one another.  Please
don’t let the fear of our perception of your home prevent you from having us over!
(Here is the "safe" part for you, the invite is all up to you as I promise we won’t just
come knocking on your door!!)
</p>
<p>
In Pastor Jason's words:  "This is not a counseling session or a time for us to secretly
'assess' you!  That feels weird just typing it out."  The reason for the visit is 100%
relational, in we just want to get to know you a least enough to have a relationship with
you.  (Another "safe" part for you is we have set these visits to be less than 1 hour in
length so we aren’t coming over to spend the night!)
</p>
<p>
PLEASE don't make us anything to eat!  We don’t want there to be any "work" on your end
and we truly don't want to be snacking after dinner as we all know how deadly that would
be on my girly figure!!
</p>
<p>
One more "safe" idea for you:  This is a voluntary thing and we PROMISE to pass no
judgement if it doesn't work for you to invite us over.
</p>

<h4 class="text-dark">Next Steps</h4>
<p><a href="/">Schedule a meeting</a></p>
<p>
NOTE:  Please understand that it may take us quite a while to get to your house because we
want to model maintaining "balance" in our lives for each of you so that we will have
margins in our lives as opposed to stress!  We believe the "slow and steady wins the
race"!!
</p>
<p>
Hope to see you soon whether that be here, there or in your home!
</p>
<p>
- Will (For Lindy and I both)
</p>
"""
        about.save()
        self.stdout.write(self.style.SUCCESS("Successfully created 'about' FAQ"))

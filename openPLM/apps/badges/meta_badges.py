from django.contrib.comments import Comment
from django.utils.translation import ugettext_lazy as _

from openPLM.plmapp.models import *

from utils import MetaBadge

class Autobiographer(MetaBadge):
    """
    Badge won by user who completed his (her) profile (first name, last name and e mail)
    """
    id = "autobiographer"
    model = UserProfile
    one_time_only = True

    title = _("Autobiographer")
    description = _("Completed the User Profile")
    level = "1"

    progress_finish = 3
        

    def get_progress(self, user):
        has_email = 1 if user.email else 0
        has_f_name = 1 if user.first_name else 0
        has_l_name = 1 if user.last_name else 0
        return has_email + has_f_name + has_l_name
        
    def check_email(self, instance):
        return instance.user.email
    
    def check_last_name(self, instance):
        return instance.user.last_name
        
    def check_first_name(self, instance):
        return instance.user.first_name
    
    def check_can_win_badge(self, instance):
        return True    


#: badges won when user cancel objects
class SerialKiller(MetaBadge):
    """
    Badge won by user who cancelled XX objects.
    (number of object set to 20 here but it can be modified)
    """
    id= "serialkiller"
    model = History
    one_time_only = True
    
    title = _("Serial Killer")
    description = _("Cancelled XX objects")
    level = "2"
    
    #assuming the badge serial killer is awarded when user has cancelled 20 objects
    progress_finish = 20
    

    def get_progress(self, user):
        cancel_hist = self.model.objects.filter(user=user,action='Cancel').count()
        return cancel_hist
        
    def check_cancelled(self, instance):
        user = instance.user
        return self.model.objects.filter(user=user, action='Cancel').count()>=self.progress_finish


#: badges won by sponsoring or delegating
class WelcomeAA(MetaBadge):
    """
    Badge won by user who sponsored at least 4 users
    """
    id = "welcomeaa"
    model = DelegationLink
    one_time_only = True
    
    title = _("Welcome A.A.")
    description = _("Sponsored 4 users")
    level = "2"
    
    progess_finish = 4
    
    def get_user(self, instance):
        return instance.delegator
        
    def get_progress(self, user):
        sponsored = self.model.objects.filter(delegator=user,role='sponsor').count()
        return sponsored
            
    def check_sponsor(self, instance):
        user = instance.delegator
        return self.model.objects.filter(delegator=user, role='sponsor').count()>=4

        
class GodFather(MetaBadge):
    """
    Badge won by user who sponsored more than 10 users 
    """
    id = "godfather"
    model = DelegationLink
    one_time_only = True
    
    title = _("God Father")
    description = _("Sponsored more than 10 users")
    level = "3"
    
    progress_finish=10
    
    def get_user(self, instance):
        return instance.delegator
        
    def get_progress(self, user):
        sponsored = self.model.objects.filter(delegator=user,role='sponsor').count()
        return sponsored
            
    def check_sponsor(self, instance):
        user = instance.delegator
        return self.model.objects.filter(delegator=user, role='sponsor').count()>=10
        
        
class DelegateSponsor(MetaBadge):
    """
    Badge won by user who delegate to his(her) sponsor 
    """
    id="delegatesponsor"
    model = DelegationLink
    one_time_only = True
    
    title = _("Who's the boss now")
    description = _("Delegate right(s) to his (her) sponsor")
    level = "3"
    
    def get_user(self, instance):
        return instance.delegator
        
    def get_progress (self, user):
        sponsor_qs = self.model.objects.filter(delegatee = user, role='sponsor')
        if not sponsor_qs :
            return 0
            
        sponsor = sponsor_qs[0].delegator
        progress = 1 if self.model.objects.filter(delegator = user, delegatee = sponsor).exists() else 0
        return progress

        
        
#: badges won by manipulating files

def string_in(src, str_list):
    """
    check if all string in str_list are in src
    """
    ret = True
    if isinstance(str_list, str):
        str_list=str_list.split(" ")
        
    for s in str_list:
        if src.find(s)==-1 :
            ret = False
            break
    return ret

def is_pony(src, file_names=None, found_name=False):
    """
    Test if src is in the file_names list
    
    :param src: file name to test
    :param file_names: list of suggested files name (pony names)
    :param found_name: if True return the file_names without the founded name 
    """
    if not file_names:
        file_names=["pinkie pie", "applejack", "twilight sparkle", "rarity", "rainbow dash", "fluttershy"]
    ret = False
    founded = ""
    for pony in file_names:
        ret = string_in(src,pony)
        if ret :
            if found_name:
                founded=pony
            break
    return ret,founded

def remove_pony(pony,pony_names):
    new_ponies=[]
    for p in pony_names:
        if p!=pony:
            new_ponies.append(p)
    return new_ponies
    
    
def has_all_pony(f_names, pony_names):
    """
    Test if a list of file names contains files named by all pony
    """ 
    if not pony_names:
        return True
        
    if not f_names or len(f_names)<len(pony_names):
        return False
        
    f_n = f_names.pop(0)
    pony, founded = is_pony(f_n, file_names=pony_names, found_name=True)
    if pony and len(pony_names)==1:
        return True
    elif pony:
        new_ponies = remove_pony(founded,pony_names)
        return has_all_pony(f_names, new_ponies)
    else:
        return has_all_pony(f_names, pony_names)
     
class PonyRider(MetaBadge):
    """
    Badge won by user who added a file named pinkie pie, applejack, twilight sparkle, rarity, rainbow dash OR fluttershy 
    """
    id="ponyrider"
    model = History
    one_time_only = True
    
    title = _("Pony Rider")
    description = _("Added a file named pinkie pie, applejack, twilight sparkle, rarity, rainbow dash or fluttershy")
    level = "2"
        
    def get_progress(self, user):
        doc_file_hist = self.model.objects.filter(user=user , action="File added")
        progress = 0
        if bool(doc_file_hist) :
            for h in doc_file_hist :
                f_name = h.details.split(" : ")[1]
                ret, f = is_pony(f_name)
                if ret :
                    progress = 1
                    break
        return progress
        
        
        
class SuperPonyRider(MetaBadge):
    """
    Badge won by users who added files named according to ALL characters from my little pony
    """
    id="superponyrider"
    model = History
    one_time_only = True
    
    title = _("Super Pony Rider")
    description = _("Added files named pinkie pie, applejack, twilight sparkle, rarity, rainbow dash and fluttershy")
    level = "4"
    
    pony_names=["pinkie pie", "applejack", "twilight sparkle", "rarity", "rainbow dash", "fluttershy"]
        
    def get_progress(self, user):
        doc_file_hist = self.model.objects.filter(user=user , action='File added')
        progress = 0
        if doc_file_hist :
            f_names = []
            for h in doc_file_hist :
                f_names.append(h.details.split(" : ")[1])
            progress = 1 if has_all_pony(f_names, self.pony_names) else 0
        return progress
        
    def check_has_added_enough_files(self, instance):
        user = instance.user
        return self.model.objects.filter(user=user, action='File added').count()>= len(self.pony_names)
        
        
        
class DragonSlayer(MetaBadge):
    """
    Badge won by user who added and destroyed a file named spike 
    """
    id = "drangonslayer"
    model = History
    one_time_only = True
    
    title = _("Dragon Slayer")
    description = _("Added and destroyed a file named spike")
    level = "4"
        
    def get_progress(self, user):
        spike_hist = self.model.objects.filter(user=user, action__startswith="File ", details__icontains=" spike.")
        if not spike_hist:
            return 0
            
        if spike_hist.filter(action="File added") and spike_hist.filter(action="File deleted"):
            progress = 1
        else:
            progress = 0
        return progress
        
    def check_has_added_and_deleted(self, instance):
        user = instance.user
        files_manip = self.model.objects.filter(user=user, action__startswith="File ")
        return bool(files_manip.filter(action="File added")) and bool(files_manip.filter(action="File deleted"))
        
        
#: badges won by user who diffused informations

class Herald(MetaBadge):
    """
    Badge won by user who notified 50 users 
    """
    id ="herald"
    model = History
    one_time_only = True
    
    title = _("Herald")
    description = _("Notified 50 users")
    level = "3"
    
    progress_finish = 50
    
    def get_progress(self, user):
        notified = self.model.objects.filter(user=user, action="New notified").count()
        return notified
        
        
        
class Journalist(MetaBadge):
    """
    Badge won by users who published XX objects.
    """
    id="journalist"
    model = History
    one_time_only = True
    
    title = _("Journalist")
    description = _("Published XX objects")
    level = "3"
    
    # until the numbers of objects to published, to won this badge , is set
    progress_finish = 20
        
    def get_progress(self, user):
        published = self.model.objects.filter(user=user, action="Publish").count()
        return published
        
    def check_can_publish(self, instance):
        """
        only user who can publish can win this badge
        """
        user = instance.user
        return user.get_profile().can_publish
        
        
#: badges won by user who created links or objects

class HiruleHero(MetaBadge):
    """
    Badge won by users who created 100 part-document links 
    """
    id="hirulehero"
    model = History
    one_time_only = True
    
    title = _("Hirule's Hero")
    description = _("Created 100 part-documents links")
    level = "3"
    
    progress_finish = 100
        
    def get_progress(self, user):
        linked = self.model.objects.filter(user=user, action="Link : document-part").count()
        return linked

        
        
#class Pacman(MetaBadge):
#    """
#    Badge won by user who created XXX files using the decomposition 
#    """
#    id="pacman"
#    model = DocumentFile
#    one_time_only = True
#    
#    title = _("Pacman")
#    description = _("Created XXX files using the decomposition")
#    level = "3"
#    
#    # until the number of files is set
#    progress_finish = 10
#    

class WelcomeToHogwarts(MetaBadge):
    """
    Create a Part named "Wizard Wand"    
    """ 
    id="welcometohogwarts"
    model = Part
    one_time_only = True
    
    title = _("Welcome To Hogwarts")
    description = _("Created a Part named `Wizard Wand`")
    level = "4"
    
    def get_user(self, instance):
        return instance.creator
        
    def get_progress(self, user):
        wizard = self.model.objects.filter(creator=user, name__icontains="Wizard Wand").exists()
        progress = 1 if wizard else 0
        return progress
        

class EmmettBrown(MetaBadge):
    """
    Create 121 parts/documents 
    """
    id="emmettbrown"
    model = History
    one_time_only = True
    
    title = _("Emmett Brown")
    description = _("Created 121 parts and documents")
    level = "4"
    
    progress_finish = 121
        
    def get_progress(self, user):
        created = Part.objects.filter(creator=user).count()
        return created
        
class Guru(MetaBadge):
    """
    Create XX groups 
    """
    id="guru"
    model = Group
    one_time_only = True
    
    title = _("Guru")
    description = _("Created XX groups")
    level = "4"
    
    progress_finish = 10
    
    def get_user(self, instance):
        return instance.creator
        
    def get_progress(self, user):
        created = self.model.objects.filter(creator=user).count()
        return created      
        
          
#: badges won manipulating object
class Archivist(MetaBadge):
    """
    Badge won by user who deprecated XX documents 
    """
    id="archivist"
    model = History
    one_time_only = True
    
    title = _("Archivist")
    description = _("Deprecated XX documents")
    level = "3"
    
    #until the number of deprecated doc is set
    progress_finish = 20
        
    def get_progress(self, user):
        deprecated = self.model.objects.filter(user=user, action="Promote", details__contains=" to deprecated").count()
        return deprecated

#class Architect(MetaBadge):
#    """
#    decompose a document into 50+ objects 
#    """
#    id="architect"
#    model = 
#    one_time_only = True
#    
#    title = _("Architect")
#    description = _("Decomposed a document into 50 objects or more")
#    level = "3"
#    
#    progress_finish = 50
#    
#    def get_user(self, instance):
#        return 
#        
#    def get_progress(self, user):
#        return 

class WisedOne(MetaBadge):
    """
    Reject 500 documents signatures 
    """
    id="wisedone"
    model = History
    one_time_only = True
    
    title = _("Wised One")
    description = _("Rejected 500 documents signatures (or demoted 500 objects)")
    level = "4"
    
    progress_finish = 10
        
    def get_progress(self, user):
        rejected = self.model.objects.filter(user=user, action="Demote").count()
        return rejected/50
        
        
class Replicant(MetaBadge):
    """
    Badge won by user who cloned a part/document 
    """
    id="replicant"
    model = History
    one_time_only = True
    
    title = _("Replicant")
    description = _("Cloned a part/document")
    level = "1"
        
    def get_progress(self, user):
        progress = 1 if self.model.objects.filter(user=user, action="Clone").exists() else 0
        return progress
        
class Frankeinstein(MetaBadge):
    """
    Badge won by user who clonee a cancelled or deprecated object 
    """
    id="frankeinstein"
    model = History
    one_time_only = True
    
    title = _("Frankeinstein")
    description = _("Cloned a cancelled or deprecated object")
    level = "2"
        
    def get_progress(self, user):
        cloned = self.model.objects.filter(user=user, action="Clone")
        if not cloned :
            return 0
        
        cloned = [c.plmobject for c in cloned if c.plmobject.is_cancelled or c.plmobject.is_deprecated]
        progress = 0 if not cloned else 1
        return progress

        
class Tipiak(MetaBadge):
    """
    Badge won by user who clonee object (s)he doesn't own/ didn't create 
    """
    id="tipiak"
    model = History
    one_time_only = True
    
    title = _("Tipiak")
    description = _("Cloned object owned and created by another user")
    level = "3"
        
    def get_progress(self, user):
        cloned = self.model.objects.filter(user=user, action="Clone")
        if not cloned :
            return 0
            
        cloned = [c for c in cloned if c.plmobject.owner != user and c.plmobject.creator != user]
        progress = 0 if not cloned else 1
        return progress
        
                        
#class Curious(MetaBadge):
#    """
#    Badge won by user who clicked on the help link 
#    """
#    id="curious"
#    model = 
#    one_time_only = True
#    
#    title = _("Curious")
#    description = _("Clicked on the help link")
#    level = "1"
#    
#    def get_user(self, instance):
#        return
#        
#    def get_progress(self, user):
#        return 
        

#: property badges        
class Materialistic(MetaBadge):
    """
    Badge won by user who owns more than 1000 objects 
    """
    id="materialistic"
    model = PLMObject
    one_time_only = True
    
    title = _("Materialistic")
    description = _("Owns more than 1000 objects")
    level = "3"
    
    progress_finish = 10
    
    def get_user(self, instance):
        return instance.owner
        
    def get_progress(self, user):
        owned = self.model.objects.filter(owner=user).count()
        return owned/100
        
        
class Popular(MetaBadge):
    """
    Badge won by user who belongs to 20 groups or more
    """
    id="popular"
    model = GroupHistory
    one_time_only = True
    
    title = _("Popular")
    description = _("Belongs to 20 groups or more")
    level = "4"
    
    progress_finish = 20
    
    def get_user(self, instance):
        if instance.action == "User added":
            user_name = instance.details
            return User.objects.get(username=user_name)
        else :
            return None
        
    def get_progress(self, user):
        if user :
            groups = GroupInfo.objects.filter(id__in=user.groups.all()).count()
            return groups
        else :
            return 0
            
    def check_can_win_badge(self, instance):
        return True

#: comment badges        
class DarthVader(MetaBadge):
    """
    Added the comment "Chocking Hazard"
    """
    id="darthvader"
    model = Comment
    one_time_only = True
    
    title =_("Darth Vader")
    description = _("Posted the comment `Chocking Hazard`")
    level = "4"
        
    def get_progress(self, user):
        comments = self.model.objects.filter(user=user).values_list('comment', flat=True)
        comments = [c.lower() for c in comments]
        progress = 1 if "chocking hazard" in comments else 0
        return progress
        
    def check_can_win_badge(self, instance):
        return True
    
    def check_has_posted_comment(self, instance):
        user = instance.user
        return self.model.objects.filter(user=user).exists()
        

def contains_smiley(src):
    #list of regex or list of smileys
    #smileys_regex =[]
    available_smileys = [" :) "," (: "]
    
    for smiley in available_smileys:
        if smiley in src:
            return True
    return False
    
                
class RadicalEdward(MetaBadge):
    """
    Post 100 :) comments
    """
    id="radicaledward"
    model = Comment
    one_time_only = True
    
    title = _("Radical Edward")
    description = _("Posted 100 :) comments")
    level = "4"
    
    progress_start = 0
    progress_finish = 100
    
    def get_user(self, instance):
        return instance.user
        
    def get_progress(self, user):
        comments = Comment.objects.filter(user=user).values_list('comment', flat=True)
        count = 0
        for c in comments:
            if ":)" in c :
                count = count +1
        return count

    def check_can_win_badge(self, instance):
        return True
    
    def check_has_posted_enough(self, instance):
        user = instance.user
        return self.model.objects.filter(user=user).count() >= self.progress_finish



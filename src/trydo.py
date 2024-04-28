import logging
from gitlab import Gitlab
from gitlab.const import AccessLevel as GlALv
from gitlab.exceptions import (
    GitlabAuthenticationError as GlAuthErr,
    GitlabCreateError as GlCreateErr,
    GitlabUpdateError as GlUpdateErr,
    GitlabDeleteError as GlDeleteErr,
    GitlabListError as GlListErr,
    GitlabGetError as GlGetErr)

logpath = "demo1.log"
logfmt = "%(asctime)s:[%(levelname)s] %(message)s"
dtfmt = "%Y/%m/%d %I:%M:%S %p"
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, filename=logpath, encoding="utf-8", format=logfmt, datefmt=dtfmt)

def retry(callback, gl:Gitlab, retry:bool=True, times:int=25, **kwargs):
    stat = None
    ret = None
    left = times
    if retry:
        left = times
        assert times > 0
    else:
        left = 1
    while left > 0:
        try:
            ret = callback(gl, **kwargs)
            assert ret
            stat = True    
            break
        except (GlAuthErr, GlCreateErr, GlUpdateErr,
                GlDeleteErr, GlListErr, GlGetErr) as e:
            logger.error(e)
            left = left - 1
            stat = False
    return stat, ret

def create_group(gl:Gitlab, **kwargs) -> int:
    """
    Input:
        gl:     Gitlab connection
        kwargs: Dict{name, path}
    Return:
        ret_gid: group id
    """
    ret_gid = -1
    try:
        group = gl.groups.create(data=kwargs)
        ret_gid = group.get_id()
        logger.info("create_group(%s) with gid('%s')", kwargs, ret_gid)
    except (GlAuthErr, GlCreateErr, GlGetErr) as e:
        raise e
    return ret_gid

def create_user(gl:Gitlab, **kwargs) -> int:
    """
    Input:
        gl:     Gitlab connection
        kwargs: Dict{name, username, email}
    Return:
        ret_uid: user id
    """
    ret_uid = -1
    info = {**kwargs,'password':'sundb231',
            'reset_password':False,
            'force_random_password':False}
    try:
        user = gl.users.create(data=info)
        ret_uid = user.get_id()
        logger.info("create_user(%s) with uid('%s')", info['name'], ret_uid)
    except (GlAuthErr, GlCreateErr, GlGetErr) as e:
        raise e
    return ret_uid

def create_member(gl:Gitlab, **kwargs):
    """
    Input:
        gl:     Gitlab connection
        kwargs: Dict{uid, gid, alv}
                // alv: access level
    Return:
        ret_uid: member id
    """
    ret_mid = -1
    gid = kwargs['gid']
    uid = kwargs['uid']
    alv = kwargs['alv']
    info = {'user_id':uid, 'access_level':alv}
    try:
        group = gl.groups.get(gid)
        member = group.members.create(data=info)
        ret_mid = member.get_id()
        logger.info("create_member(uid:'%s',gid:'%s') with mid('%s')", uid, gid, ret_mid)
    except (GlAuthErr, GlGetErr, GlCreateErr) as e:
        raise e
    return ret_mid

def update_user_role(gl:Gitlab, **kwargs) -> bool:
    stat = None
    try:
        uid = kwargs['uid']
        admin = kwargs['admin']
        user = gl.users.get(uid)
        assert user
        if admin:
            user.attributes['highest_role'] = GlALv.ADMIN
        user.save()
        stat = True
    except (GlUpdateErr, GlGetErr, GlAuthErr) as e:
        raise e
    return stat

def remove_user(gl:Gitlab, **kwargs) -> bool:
    stat = None
    try:
        uid = kwargs['uid']
        gl.users.delete(id=uid, hard_delete=True)
        stat = True
        logger.info("remove_user(%s)", kwargs)
    except (GlAuthErr, GlDeleteErr) as e:
        raise e
    return stat

if __name__ == "__main__":
    global_url = "http://10.20.4.136:82"
    global_pat = "glpat-A88kkCnryEx8G_3NcFFs"

    gl = Gitlab(url=global_url, private_token=global_pat)

    # rc, gid = retry(create_group, gl=gl, name='tg8', path='tg8')
    # assert rc

    # rc, uid = retry(create_user, gl=gl, name='tu8', username='tu8', email='tu8@test.com')
    # assert rc

    # rc, mid = retry(create_member, gl=gl, uid=uid, gid=gid, alv=GlALv.DEVELOPER)
    # assert rc

    # rc, stat = retry(update_user_role, gl, uid=89, admin=True)
    # assert rc
    rc, stat = retry(remove_user, gl=gl, uid=93)
    assert rc
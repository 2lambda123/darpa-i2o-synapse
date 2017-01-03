from synapse.tests.common import *

import synapse.cortex as s_cortex
import synapse.lib.userauth as s_userauth

class UserAuthTest(SynTest):

    def test_userauth_base(self):
        core = s_cortex.openurl('ram:///')
        auth = s_userauth.UserAuth(core)

        auth.addUser('visi')
        auth.addRole('root')

        self.assertRaises( DupUser, auth.addUser, 'visi' )
        self.assertRaises( DupRole, auth.addRole, 'root' )

        auth.addUserRule('visi','foo.*')
        auth.addRoleRule('root','baz.*')

        self.assertRaises( NoSuchUser, auth.addUserRule, 'newp', 'haha.*' )
        self.assertRaises( NoSuchRole, auth.addRoleRule, 'newp', 'haha.*' )

        self.assertTrue( auth.isUserAllowed('visi','foo.bar') )
        self.assertFalse( auth.isUserAllowed('visi','baz.faz') )

        auth.addUserRole('visi','root')

        self.assertEqual( auth.getUserRoles('visi')[0], 'root' )

        self.assertTrue( auth.isUserAllowed('visi','foo.bar') )
        self.assertTrue( auth.isUserAllowed('visi','baz.faz') )

        auth.delUserRole('visi','root')

        self.assertTrue( auth.isUserAllowed('visi','foo.bar') )
        self.assertFalse( auth.isUserAllowed('visi','baz.faz') )

        # put the userrole back so we can delete the role...
        auth.addUserRole('visi','root')

        self.assertTrue( auth.isUserAllowed('visi','foo.bar') )
        self.assertTrue( auth.isUserAllowed('visi','baz.faz') )

        auth.delRole('root')

        self.assertTrue( auth.isUserAllowed('visi','foo.bar') )
        self.assertFalse( auth.isUserAllowed('visi','baz.faz') )

        core.fini()
        auth.fini()

    def test_userauth_rules(self):
        core = s_cortex.openurl('ram:///')
        auth = s_userauth.UserAuth(core)

        auth.addUser('visi')
        auth.addUserRule('visi','foo.*')

        rules = s_userauth.Rules(auth,'visi')

        self.assertTrue( rules.allow('foo.bar') )
        self.assertFalse( rules.allow('baz.faz') )

        auth.addUserRule('visi','baz.*')

        self.assertTrue( rules.allow('foo.bar') )
        self.assertTrue( rules.allow('baz.faz') )

        auth.delUserRule('visi','foo.*')

        self.assertFalse( rules.allow('foo.bar') )
        self.assertTrue( rules.allow('baz.faz') )

        auth.fini()
        core.fini()

    def test_userauth_scope(self):
        core = s_cortex.openurl('ram:///')
        auth = s_userauth.UserAuth(core)

        auth.addUser('visi')
        auth.addUserRule('visi','foo:*')

        self.eq( s_userauth.getSynUser(), None )
        self.eq( s_userauth.getSynAuth(), None )

        self.assertFalse( s_userauth.amIAllowed('foo:bar') )
        self.assertTrue( s_userauth.amIAllowed('foo:bar', onnone=True) )

        with s_userauth.asSynUser('visi',auth=auth):

            self.eq( s_userauth.getSynUser(), 'visi' )
            self.assertIsNotNone( s_userauth.getSynAuth() )

            self.assertTrue( s_userauth.amIAllowed('foo:bar') )
            self.assertFalse( s_userauth.amIAllowed('derp:bar') )

        self.eq( s_userauth.getSynUser(), None )
        self.eq( s_userauth.getSynAuth(), None )

        with s_userauth.asSynUser('newp',auth=auth):

            self.eq( s_userauth.getSynUser(), 'newp' )
            self.assertIsNotNone( s_userauth.getSynAuth() )
            self.assertRaises( NoSuchUser, s_userauth.amIAllowed, 'foo:bar' )

        self.eq( s_userauth.getSynUser(), None )
        self.eq( s_userauth.getSynAuth(), None )

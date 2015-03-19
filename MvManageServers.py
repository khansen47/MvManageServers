import sublime, sublime_plugin
import json
import urllib

class TakeServerCommand( sublime_plugin.WindowCommand ):
	def run( self ):
		server_list	= []
		settings	= sublime.load_settings( 'MvManageServers.sublime-settings' )
		self.login	= str( settings.get( 'Bugzilla_login' ) )
		self.cookie	= str( settings.get( 'Bugzilla_logincookie' ) )

		if self.login == '':
			return sublime.message_dialog( 'Missing Bugzilla login setting' )

		if self.cookie == '':
			return sublime.message_dialog( 'Missing Bugzilla login cookie setting' )

		result, response, error = make_json_request( 'Servers_Current_Status', self.login, self.cookie )

		if not result:
			return sublime.error_message( error )

		server_list = sorted( response[ 'data' ][ 'available_servers' ] + response[ 'data' ][ 'available_tunnel_servers' ], key = lambda k: k[ 'hostname' ] )

		if len( server_list ) == 0:
			return sublime.message_dialog( 'No servers available to check out' )

		self.show_quick_panel( [ server[ 'hostname' ] for server in server_list ], lambda index: self.server_select_callback( server_list, index ) )

	def server_select_callback( self, server_list, index ):
		if index == -1:
			return

		server = server_list[ index ]

		result, response, error = make_json_request( 'Server_Take', self.login, self.cookie, str( server[ 'id' ] ) )

		if not result:
			return sublime.error_message( error )

		return sublime.status_message( 'Server ' + server[ 'hostname' ] + ' taken' )

	def show_quick_panel( self, entries, on_select, on_highlight = None ):
		sublime.set_timeout( lambda: self.window.show_quick_panel( entries, on_select, on_highlight = on_highlight ), 10 )

class ReleaseServerCommand( sublime_plugin.WindowCommand ):
	def run( self ):
		server_list			= []
		my_servers			= []
		settings			= sublime.load_settings( 'MvManageServers.sublime-settings' )
		self.login			= str( settings.get( 'Bugzilla_login' ) )
		self.cookie			= str( settings.get( 'Bugzilla_logincookie' ) )

		if self.login == '':
			return sublime.message_dialog( 'Missing Bugzilla login setting' )

		if self.cookie == '':
			return sublime.message_dialog( 'Missing Bugzilla login cookie setting' )

		result, response, error = make_json_request( 'Servers_Current_Status', self.login, self.cookie )

		if not result:
			return sublime.error_message( error )

		server_list = sorted( response[ 'data' ][ 'unavailable_servers' ], key = lambda k: k[ 'hostname' ] )
		user_id		= response[ 'data' ][ 'user_id' ]

		for server in server_list:
			if server[ 'user_id' ] == user_id:
				my_servers.append( server )

		if len( my_servers ) == 0:
			return sublime.message_dialog( 'You have no servers checked out' )

		self.show_quick_panel( [ '{0} - {1}' . format( server[ 'hostname' ], server[ 'formatted_time' ] ) for server in my_servers ], lambda index: self.server_select_callback( my_servers, index ) )

	def server_select_callback( self, server_list, index ):
		if index == -1:
			return

		server = server_list[ index ]

		result, response, error = make_json_request( 'Server_Release', self.login, self.cookie, str( server[ 'id' ] ) )

		if not result:
			return sublime.error_message( error )

		return sublime.status_message( 'Server ' + server[ 'hostname' ] + ' released' )

	def show_quick_panel( self, entries, on_select, on_highlight = None ):
		sublime.set_timeout( lambda: self.window.show_quick_panel( entries, on_select, on_highlight = on_highlight ), 10 )

#
# Helper Functions
#

def make_json_request( function, login, cookie, server_id = 0 ):
	params 	= urllib.parse.urlencode( { 'Function': function, 'server_id': server_id } ).encode( 'utf-8' )
	req 	= urllib.request.Request( url 		= 'https://bugzilla.dev.mivamerchant.com/servers/devservers.php',
									  data 		= params,
									  headers 	= { 'Cookie': 'Bugzilla_login=' + login + '; Bugzilla_logincookie=' + cookie + ';' } )

	try:
		request = urllib.request.urlopen( req )
	except Exception as e:
		print( 'Failed opening URL: {0}' . format( str( e ) ) )
		return False, None, 'Failed to open URL'

	try:
		content = request.read().decode( 'utf-8-sig' )
	except Exception as e:
		print( 'Failed decoding response: {0}' . format( str( e ) ) )
		return False, None, 'Failed to decode response'

	try:
		json_response 	= json.loads( content )
	except Exception as e:
		print( 'Failed to parse JSON: {0}' . format( str( e ) ) )
		return False, None, 'Failed to parse JSON response'

	if 'success' not in json_response or json_response[ 'success' ] != 1:
		print( 'JSON response was not a success {0}' . format( json_response ) )
		return False, None, json_response[ 'error_message' ]

	return True, json_response, None

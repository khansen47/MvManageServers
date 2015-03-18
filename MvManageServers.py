import sublime, sublime_plugin
import json
import urllib

class TakeServerCommand( sublime_plugin.WindowCommand ):
	def run( self ):
		servers 		= []
		settings		= sublime.load_settings( 'MvManageServers.sublime-settings' )
		self.login		= str( settings.get( 'Bugzilla_login' ) )
		self.cookie		= str( settings.get( 'Bugzilla_logincookie' ) )

		if self.login == '':
			return sublime.status_message( 'Missing Bugzilla login setting' )

		if self.cookie == '':
			return sublime.status_message( 'Missing Bugzilla login cookie setting' )

		result, response, error = make_json_request( 'Servers_Current_Status', self.login, self.cookie )

		if not result:
			return sublime.error_message( error )

		server_list = response[ 'data' ][ 'available_servers' ] + response[ 'data' ][ 'available_tunnel_servers' ]

		for server in server_list:
			servers.append( server[ 'hostname' ] )

		if len( servers ) == 0:
			return sublime.status_message( 'No servers available to check out' )

		self.show_quick_panel( servers, lambda index: self.server_select_callback( server_list, servers, index ) )

	def server_select_callback( self, server_list, servers, index ):
		if index == -1:
			return

		for server in server_list:
			if server[ 'hostname' ] == servers[ index ]:
				server_id = server[ 'id' ]

		result, response, error = make_json_request( 'Server_Take', self.login, self.cookie, str( server_id ) )

		if not result:
			return sublime.error_message( error )

		return sublime.status_message( 'Server ' + servers[ index ] + ' taken' )

	def show_quick_panel( self, entries, on_select, on_highlight = None ):
		sublime.set_timeout( lambda: self.window.show_quick_panel( entries, on_select, on_highlight = on_highlight ), 10 )

class ReleaseServerCommand( sublime_plugin.WindowCommand ):
	def run( self ):
		servers 		= []
		settings		= sublime.load_settings( 'MvManageServers.sublime-settings' )
		self.login		= str( settings.get( 'Bugzilla_login' ) )
		self.cookie		= str( settings.get( 'Bugzilla_logincookie' ) )

		if self.login == '':
			return sublime.status_message( 'Missing Bugzilla login setting' )

		if self.cookie == '':
			return sublime.status_message( 'Missing Bugzilla login cookie setting' )

		result, response, error = make_json_request( 'Servers_Current_Status', self.login, self.cookie )

		if not result:
			return sublime.error_message( error )

		server_list = response[ 'data' ][ 'unavailable_servers' ]
		user_id		= response[ 'data' ][ 'user_id' ]

		for server in server_list:
			if server[ 'user_id' ] == user_id:
				servers.append( server[ 'hostname' ] )

		if len( servers ) == 0:
			return sublime.status_message( 'You have no servers checked out' )

		self.show_quick_panel( servers, lambda index: self.server_select_callback( server_list, servers, index ) )

	def server_select_callback( self, server_list, servers, index ):
		if index == -1:
			return

		for server in server_list:
			if server[ 'hostname' ] == servers[ index ]:
				server_id = server[ 'id' ]

		result, response, error = make_json_request( 'Server_Release', self.login, self.cookie, str( server_id ) )

		if not result:
			return sublime.error_message( error )

		return sublime.status_message( 'Server ' + servers[ index ] + ' released' )

	def show_quick_panel( self, entries, on_select, on_highlight = None ):
		sublime.set_timeout( lambda: self.window.show_quick_panel( entries, on_select, on_highlight = on_highlight ), 10 )


#
# Helper Functions
#
def make_json_request( function, login, cookie, server_id = 0 ):
	params 	= urllib.parse.urlencode( { 'Function': function, 'server_id': server_id } )
	params 	= params.encode( 'utf-8' )
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

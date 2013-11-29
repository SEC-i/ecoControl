require 'sinatra'

api_base = 'http://172.16.19.114/api/switches/'

get '/' do
	erb :index
end

get '/api/' do
	'Hello world!'
end

get '/:switch_number/:switch_state' do
	if params[:switch_number] == "red" or params[:switch_number] == "green"
		number = (params[:switch_number]  == 'red' ? '1' : '2')
		state = (params[:switch_state]  == 'on' ? 'on' : 'off')
		system( 'curl ' + api_base + ' -d "api_key=s3cr3t&switch_number=' + number + '&switch_state=' + state + '" -X POST' )
		(params[:switch_number]  == 'red' ? 'red' : 'green') + ' ' + (params[:switch_state]  == 'on' ? 'on' : 'off')
	else
		'error'
	end
end

configure do
  set :port, '8000'
  set :bind, '0.0.0.0'
  set :public_folder, File.dirname(__FILE__) + '/static'
end
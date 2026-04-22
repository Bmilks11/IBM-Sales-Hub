#!/usr/bin/env ruby
# Syncs local send_log.json -> kpi_log.json and pipeline.json, then pushes to GitHub.
# Run after each outreach session: ruby scripts/sync_dashboard.rb

require 'json'
require 'date'
require 'base64'
require 'net/http'
require 'uri'

TOKEN = ENV['GITHUB_TOKEN'] || File.read(File.expand_path('~/.ibm_hub_token')).strip rescue ''
OWNER = 'Bmilks11'
REPO  = 'IBM-Sales-Hub'
BASE  = File.expand_path('..', __dir__)

def github_put(token, path, content, message)
  uri = URI("https://api.github.com/repos/#{OWNER}/#{REPO}/contents/#{path}")
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true
  # Get current SHA
  req = Net::HTTP::Get.new(uri)
  req['Authorization'] = "token #{token}"
  req['Accept'] = 'application/vnd.github.v3+json'
  resp = http.request(req)
  sha = JSON.parse(resp.body)['sha'] rescue nil
  # PUT
  req2 = Net::HTTP::Put.new(uri)
  req2['Authorization'] = "token #{token}"
  req2['Content-Type'] = 'application/json'
  body = { message: message, content: Base64.strict_encode64(content) }
  body[:sha] = sha if sha
  req2.body = body.to_json
  resp2 = http.request(req2)
  JSON.parse(resp2.body)['content'] ? puts("  OK #{path}") : puts("  FAIL #{path}: #{resp2.body[0..80]}")
end

today = Date.today.to_s
send_log_path = File.join(BASE, 'data', 'send_log.json')
kpi_path      = File.join(BASE, 'data', 'kpi_log.json')
pipeline_path = File.join(BASE, 'data', 'pipeline.json')
prospects_path = File.join(BASE, 'data', 'prospects.json')

# Load send log
send_log = File.exist?(send_log_path) ? JSON.parse(File.read(send_log_path)) : {'date'=>'','count'=>0,'sent'=>[]}

# Load existing KPI
kpi = File.exist?(kpi_path) ? JSON.parse(File.read(kpi_path)) : {
  'last_updated' => '', 'today' => {'date'=>today,'sent'=>0},
  'totals' => {'sent'=>0,'replied'=>0,'meetings_booked'=>0,'accounts_contacted'=>0},
  'weekly' => {}
}

# Update today's count
sent_today = send_log['date'] == today ? send_log['count'].to_i : 0
kpi['today'] = {'date' => today, 'sent' => sent_today}

# Update weekly (last 7 days)
7.times do |i|
  d = (Date.today - i).to_s
  kpi['weekly'] ||= {}
  kpi['weekly'][d] ||= 0
end
kpi['weekly'][today] = sent_today

# Update totals from all sent entries
all_sent = send_log['sent'] || []
unique_companies = all_sent.map{|e| e['company']}.uniq.length
kpi['totals']['sent'] = send_log['count'].to_i
kpi['totals']['accounts_contacted'] = unique_companies
kpi['last_updated'] = Time.now.utc.strftime('%Y-%m-%dT%H:%M:%SZ')

# Load existing pipeline or build from sent
pipeline = File.exist?(pipeline_path) ? JSON.parse(File.read(pipeline_path)) : []
pipeline_by_company = pipeline.each_with_object({}) {|p,h| h[p['company']] = p}

# Load prospects for industry/city data
prospects = File.exist?(prospects_path) ? JSON.parse(File.read(prospects_path)) : []
prospect_map = prospects.each_with_object({}) {|p,h| h[p['company']] = p}

# Add newly sent accounts to pipeline
all_sent.each do |entry|
  co = entry['company']
  next if pipeline_by_company[co]
  prospect = prospect_map[co] || {}
  pipeline_by_company[co] = {
    'company'        => co,
    'status'         => 'contacted',
    'industry'       => prospect['industry'] || '',
    'city'           => prospect['city'] || '',
    'tier'           => prospect['tier'] || 2,
    'product'        => 'Planning Analytics',
    'last_contacted' => entry['sent_at'] || today,
    'reply_date'     => nil,
    'meeting_date'   => nil,
    'notes'          => ''
  }
end

new_pipeline = pipeline_by_company.values.sort_by{|p| p['last_contacted'] || ''}.reverse

# Write locally
File.write(kpi_path, JSON.pretty_generate(kpi))
File.write(pipeline_path, JSON.pretty_generate(new_pipeline))

puts "KPI: #{kpi['totals']['sent']} sent | #{kpi['totals']['replied']} replied | #{kpi['totals']['meetings_booked']} meetings"
puts "Pipeline: #{new_pipeline.length} accounts"

# Push to GitHub
if TOKEN.empty?
  puts "\nNo GITHUB_TOKEN found. Set it in .env or ~/.ibm_hub_token to auto-push."
  puts "Dashboard data saved locally only."
else
  puts "\nPushing to GitHub..."
  github_put(TOKEN, 'data/kpi_log.json', JSON.pretty_generate(kpi), 'Sync KPI dashboard data')
  github_put(TOKEN, 'data/pipeline.json', JSON.pretty_generate(new_pipeline), 'Sync pipeline data')
  puts "Dashboard updated: https://bmilks11.github.io/IBM-Sales-Hub/dashboard/"
end

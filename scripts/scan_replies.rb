#!/usr/bin/env ruby
# Scans Outlook inbox for replies to IBM Sales Hub outreach.
# Updates pipeline.json status to 'replied' for matching companies.
# Run: ruby scripts/scan_replies.rb

require 'json'
require 'open3'

BASE = File.expand_path('..', __dir__)
pipeline_path = File.join(BASE, 'data', 'pipeline.json')
send_log_path = File.join(BASE, 'data', 'send_log.json')

pipeline = File.exist?(pipeline_path) ? JSON.parse(File.read(pipeline_path)) : []
send_log = File.exist?(send_log_path) ? JSON.parse(File.read(send_log_path)) : {'sent'=>[]}

# Get sent email addresses from log
sent_emails = (send_log['sent'] || []).map{|e| e['to']}.compact.uniq

# AppleScript to get recent inbox messages
script = <<~APPLE
  tell application "Microsoft Outlook"
    set inbox to inbox
    set msgs to messages of inbox
    set output to ""
    repeat with m in (items 1 thru (count of msgs) of msgs)
      if (count of msgs) > 200 then exit repeat
      set senderAddr to address of sender of m
      set subj to subject of m
      set recvDate to time received of m
      set output to output & senderAddr & "|" & subj & "|" & (recvDate as string) & "\n"
    end repeat
    return output
  end tell
APPLE

puts "Scanning Outlook inbox..."
stdout, stderr, status = Open3.capture3('osascript', '-e', script)

if !status.success? || stdout.strip.empty?
  puts "Could not read Outlook inbox: #{stderr.strip}"
  exit 1
end

# Parse inbox messages
inbox = stdout.strip.split("\n").map do |line|
  parts = line.split("|")
  {email: parts[0].to_s.strip.downcase, subject: parts[1].to_s, date: parts[2].to_s}
end

# Match replies against sent emails
replied_emails = inbox.map{|m| m[:email]}.uniq & sent_emails.map(&:downcase)

# Update pipeline
updated = 0
pipeline.each do |account|
  next if account['status'] == 'replied' || account['status'] == 'meeting'
  sent_entry = (send_log['sent'] || []).find{|e| e['company'] == account['company']}
  next unless sent_entry
  if replied_emails.include?(sent_entry['to'].to_s.downcase)
    account['status'] = 'replied'
    account['reply_date'] = Time.now.utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    updated += 1
    puts "  REPLIED: #{account['company']}"
  end
end

File.write(pipeline_path, JSON.pretty_generate(pipeline))
puts "\nScan complete. #{replied_emails.length} replies found. #{updated} pipeline records updated."
puts "Run ruby scripts/sync_dashboard.rb to push updates to the dashboard."

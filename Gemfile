source "https://rubygems.org"

ruby File.read(".ruby-version").strip

gem "jekyll", "~> 4.3.0"
gem "csv"
gem "logger"
gem "base64"

# Theme: Chirpy
gem "jekyll-theme-chirpy", "~> 7.6"

group :jekyll_plugins do
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
  gem "jekyll-paginate"
  gem "jekyll-polyglot", "~> 1.9"
end

platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]
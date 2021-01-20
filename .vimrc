" Have syntax highlighting turned on by default.
syntax on


" Have relative line numbering turned on by efault.
set relativenumber
set nu
" Number of visual spaces per tab. When vim opens a files and reads a TAB character, it uses that many spaces to visually show the TAB.
set tabstop=4
" Number of spaces in tab when editing. This value is the number of spaces that is inserted when you hit TAB and also the number of spaces that are removed when you backspace. 
set softtabstop=4
" tabs are spaces
set expandtab
" To change the number of space characters inserted for indentation
set shiftwidth=4
" Load filetype-specific indent files
filetype indent on
set smartindent


""""" UI config
" Highlight current line
set cursorline
" Visual autocomplete for command menu

""""" Search
" Search as characters are entered
set incsearch
" Highlight matches
set nohlsearch
set bg=dark





" To add more configuration below.
" To enable auto-complete every time a HTML file is opened
autocmd FileType html set omnifunc=htmlcomplete#CompleteTags

" Enable omni completion
filetype plugin on
set omnifunc=syntaxcomplete#Complete

set noerrorbells
" Start shifting screen when 8 lines away from edge, either top or bottom
set scrolloff=10

inoremap jk <Esc>
inoremap kj <Esc>










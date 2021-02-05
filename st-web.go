package main

import (
	"encoding/xml"
	// "fmt"
	"html/template"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	// "regexp"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"strings"
)

type Child struct {
	IsDir bool
	Name  string
	Path  string
}

type STFolder struct {
	Id    string `xml:"id,attr"`
	Label string `xml:"label,attr"`
	Path  string `xml:"path,attr"`
}

type STConfig struct {
	Folders []STFolder `xml:"folder"`
}

type PageContext struct {
	ActiveFolder string
	Children     *[]Child
	Folders      *[]STFolder
	Path         string
}

type ServerContext struct {
	echo.Context
	Folders *[]STFolder
}

type Template struct {
	T *template.Template
}

func (t *Template) Render(w io.Writer,
	name string,
	data interface{},
	c echo.Context,
) error {
	return t.T.ExecuteTemplate(w, name, data)
}

func main() {
	configDir := ReadXDGConfig()
	stConfig, err := LoadSTConfig(configDir)

	if err != nil {
		log.Fatal("Unable to load Syncthing config")
	}

	t := &Template{T: template.Must(template.ParseGlob("templates/*.html"))}

	server := echo.New()

	server.Use(func(next echo.HandlerFunc) echo.HandlerFunc {
		return func(c echo.Context) error {
			cc := &ServerContext{c, &stConfig.Folders}
			return next(cc)
		}
	})

	server.Pre(middleware.RemoveTrailingSlash())

	server.Renderer = t

	server.GET("/", Home)
	server.GET("/files", Files)
	server.GET("/files/:folderId", Files)
	server.GET("/files/:folderId/*", Files)
	server.Static("/static", "assets")

	server.Logger.Fatal(server.Start(":8400"))
}

func Files(context echo.Context) error {
	folder, _ := url.QueryUnescape(context.Param("folderId"))
	path, _ := url.QueryUnescape(context.Param("*"))

	c := context.(*ServerContext)

	data := &PageContext{
		ActiveFolder: folder,
		Children:     ReadDirContent(folder, path),
		Folders:      c.Folders,
		Path:         path,
	}

	log.Println(folder, path)
	log.Println(data.ActiveFolder)
	log.Println(data.Children)
	log.Println(data.Folders)
	log.Println(data.Path)

	return context.Render(http.StatusOK, "home.html", data)
}

func Home(context echo.Context) error {
	return context.Redirect(http.StatusSeeOther, "/files")
}

func LoadConfig() {}

func LoadSTConfig(configDir string) (config STConfig, err error) {
	stConfigPath := filepath.Join(configDir, "syncthing/config.xml")
	stConfigFile, oserr := os.Open(stConfigPath)

	if oserr != nil {
		err = oserr
		return
	}

	raw, ioerr := ioutil.ReadAll(stConfigFile)

	if ioerr != nil {
		err = ioerr
		return
	}

	xml.Unmarshal(raw, &config)

	return
}

func ReadDirContent(folder string, path string) (children *[]Child) {
	if folder == "" {
		return
	}
	return
}

func ReadXDGConfig() string {
	configDir := ""
	var home string

	for _, e := range os.Environ() {
		pair := strings.SplitN(e, "=", 2)
		if pair[0] == "HOME" {
			home = pair[1]
		}
		if pair[0] == "XDG_CONFIG_HOME" {
			configDir = pair[1]
		}
	}

	if configDir != "" {
		return configDir
	}

	return filepath.Join(home, ".config")
}

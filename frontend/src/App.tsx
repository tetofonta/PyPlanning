import {GraphCanvas, recommendLayout} from "reagraph"
import {useState} from "react";
import {AppBar, IconButton, Toolbar, Typography} from "@mui/material";
import {Add as AddIcon} from "@mui/icons-material"
import "./style/app.sass"

function App() {

    const [nodes, setNodes] = useState([
        {
            id: 'n-1',
            label: '1'
        },
        {
            id: 'n-2',
            label: '2'
        }
    ])

    const [edges] = useState([
        {
            id: '1->2',
            source: 'n-1',
            target: 'n-2',
            label: 'Edge 1-2'
        }
    ])

    const layout = recommendLayout(nodes, edges);

    return (
        <>
            <AppBar className="navbar" position="static">
                <Toolbar>
                    <Typography
                        variant="h6"
                        noWrap
                        component="a"
                        sx={{
                            mr: 2,
                            display: {xs: 'none', md: 'flex'},
                            fontFamily: 'monospace',
                            fontWeight: 700,
                            letterSpacing: '.3rem',
                            textDecoration: 'none',
                        }}
                    >
                        AI-ROB
                    </Typography>
                    <div className="toolbar">
                        <IconButton style={{color: "#FFF"}} onClick={() => setNodes(n => [...n, {id: Math.random() + "", label: "PIPPO"}])}>
                            <AddIcon/>
                        </IconButton>
                    </div>
                </Toolbar>
            </AppBar>
            <div className="graph" style={{position: 'relative'}}>
                <GraphCanvas
                    nodes={nodes}
                    edges={edges}
                    layoutType={layout}
                    draggable
                />
            </div>
        </>
    )
}

export default App

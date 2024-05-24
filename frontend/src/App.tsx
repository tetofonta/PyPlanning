import {GraphCanvas, recommendLayout} from "reagraph"
import {AppBar, IconButton, Toolbar, Typography} from "@mui/material";
import "./style/app.sass"
import {NodeMenu} from "./NodeMenu.tsx";
import {NodeContextProvider, useNodeContext} from "./NodeContext.tsx";
import AddIcon from "@mui/icons-material/Add"

const Content = () => {
    const nodeContext = useNodeContext()
    const layout = recommendLayout(nodeContext.nodes, nodeContext.edges);

    return <>
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
                    <IconButton style={{color: "#FFF"}}>
                        <AddIcon/>
                    </IconButton>
                </div>
            </Toolbar>
        </AppBar>
        <div className="graph" style={{position: 'relative'}}>
            <GraphCanvas
                nodes={nodeContext.nodes}
                edges={nodeContext.edges}
                layoutType={layout}
                contextMenu={({data, onClose}) => <NodeMenu nodeContext={nodeContext} node={data as any}
                                                            onClose={onClose}/>}
                draggable
            />
        </div>
    </>
}

function App() {


    return (
        <NodeContextProvider>
            <Content/>
        </NodeContextProvider>
    )
}

export default App
